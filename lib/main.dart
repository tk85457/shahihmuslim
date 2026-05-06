import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'theme/app_theme.dart';
import 'core/router.dart';
import 'features/settings/settings_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize sqflite for web or desktop
  if (kIsWeb) {
    databaseFactory = databaseFactoryFfiWeb;
  } else if (Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  }

  final prefs = await SharedPreferences.getInstance();

  runApp(
    ProviderScope(
      overrides: [sharedPreferencesProvider.overrideWithValue(prefs)],
      child: const SahihMuslimApp(),
    ),
  );
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
