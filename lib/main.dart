import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'theme/app_theme.dart';
import 'core/router.dart';
import 'features/settings/settings_provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      systemNavigationBarColor: Colors.transparent,
    ),
  );

  // Cheap, synchronous factory wiring for web/desktop — no I/O, safe to run
  // before the first frame.
  if (kIsWeb) {
    databaseFactory = databaseFactoryFfiWeb;
  } else if (Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  }

  // COLD START FIX: previously main() awaited SharedPreferences.getInstance()
  // before ever calling runApp(), which delays the first frame Android
  // measures for cold start / "time to initial display". runApp() now fires
  // immediately; SharedPreferences loads behind a near-instant loading frame.
  runApp(const _Bootstrap());
}

/// Loads [SharedPreferences] before mounting the real app. This is fast
/// (no large I/O), so this shows for at most a frame or two — but doing it
/// here (instead of blocking main()) lets Flutter draw its first frame
/// immediately, which is what fixes slow/cold app starts.
class _Bootstrap extends StatelessWidget {
  const _Bootstrap();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<SharedPreferences>(
      future: SharedPreferences.getInstance(),
      builder: (context, snapshot) {
        final prefs = snapshot.data;
        if (prefs == null) {
          return const _BootLoading();
        }
        return ProviderScope(
          overrides: [sharedPreferencesProvider.overrideWithValue(prefs)],
          child: const SahihMuslimApp(),
        );
      },
    );
  }
}

/// Neutral loading background shown for the brief moment before
/// SharedPreferences resolves, avoiding a flash of white/unstyled content.
class _BootLoading extends StatelessWidget {
  const _BootLoading();

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: Color(0xFF311B92),
        body: SizedBox.shrink(),
      ),
    );
  }
}

class SahihMuslimApp extends ConsumerWidget {
  const SahihMuslimApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);

    final primaryColor = AppTheme.getPrimaryColor(settings.uiColor);

    return MaterialApp.router(
      title: 'Sahih Muslim',
      debugShowCheckedModeBanner: false,
      theme: settings.isDarkMode
          ? AppTheme.darkTheme(primaryColor)
          : AppTheme.lightTheme(primaryColor),
      routerConfig: goRouter,
    );
  }
}
