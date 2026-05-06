import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../theme/app_theme.dart';
import '../../data/repositories/hadith_repository.dart';
import '../../domain/models/models.dart';
import '../settings/settings_provider.dart';

final chapterHadithsListProvider = FutureProvider.family<List<Hadith>, int>((
  ref,
  chapterId,
) async {
  final repo = ref.watch(hadithRepositoryProvider);
  return repo.getHadithsByChapter(chapterId, limit: 10000);
});

final singleChapterProvider = FutureProvider.family<Chapter?, int>((
  ref,
  chapterId,
) async {
  final repo = ref.watch(hadithRepositoryProvider);
  return repo.getChapterById(chapterId);
});

class HadithListScreen extends ConsumerStatefulWidget {
  final int chapterId;
  const HadithListScreen({super.key, required this.chapterId});

  @override
  ConsumerState<HadithListScreen> createState() => _HadithListScreenState();
}

class _HadithListScreenState extends ConsumerState<HadithListScreen> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  int get chapterId => widget.chapterId;

  @override
  Widget build(BuildContext context) {
    final hadithsAsync = ref.watch(chapterHadithsListProvider(chapterId));
    final chapterAsync = ref.watch(singleChapterProvider(chapterId));
    final settings = ref.watch(settingsProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: chapterAsync.when(
          data: (chapter) => Text(
            settings.titleLanguage == 'English'
                ? (chapter?.titleEnglish ?? 'Chapter')
                : settings.titleLanguage == 'Arabic'
                ? (chapter?.titleArabic ?? 'باب')
                : (chapter?.titleUrdu ?? 'باب'),
            style: AppTheme.safeGetFont(
              settings.titleLanguage == 'English'
                  ? settings.englishFontFamily
                  : settings.titleLanguage == 'Arabic'
                  ? settings.arabicFontFamily
                  : settings.urduFontFamily,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          loading: () => const Text('Loading...'),
          error: (_, _) => const Text('Error'),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.find_in_page),
            tooltip: 'Find Hadith by Number',
            onPressed: () => _showFindDialog(context, chapterId),
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/home/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            margin: const EdgeInsets.all(12),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            decoration: BoxDecoration(
              color: isDark ? AppTheme.cardDark : Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey.shade300),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    textAlign: TextAlign.right,
                    textDirection: TextDirection.rtl,
                    keyboardType: TextInputType.number,
                    onSubmitted: (query) {
                      final trimmed = query.trim();
                      if (trimmed.isNotEmpty) {
                        _jumpByNumber(context, trimmed, chapterId);
                      }
                    },
                    decoration: InputDecoration(
                      hintText: 'حدیث نمبر لکھیں اور Enter دبائیں',
                      hintStyle: TextStyle(
                        color: isDark ? Colors.grey.shade500 : Colors.grey.shade400,
                        fontSize: 13,
                      ),
                      border: InputBorder.none,
                    ),
                  ),
                ),
                GestureDetector(
                  onTap: () {
                    final trimmed = _searchController.text.trim();
                    if (trimmed.isNotEmpty) {
                      _jumpByNumber(context, trimmed, chapterId);
                    }
                  },
                  child: const Icon(Icons.search, color: Colors.blue),
                ),
              ],
            ),
          ),
          Expanded(
            child: hadithsAsync.when(
              loading: () => Center(
                child: CircularProgressIndicator(color: Theme.of(context).primaryColor),
              ),
              error: (e, st) => Center(child: Text('Error: $e')),
              data: (hadiths) {
                if (hadiths.isEmpty) {
                  return Center(
                    child: Text(
                      'عذر خواہ ہیں، کوئی حدیث نہیں ملی',
                      style: TextStyle(color: isDark ? Colors.white70 : Colors.black87),
                    ),
                  );
                }
                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  itemCount: hadiths.length,
                  itemBuilder: (context, index) {
                    return GestureDetector(
                      onTap: () {
                        context.push('/home/chapter/$chapterId?startIndex=$index');
                      },
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
                        decoration: BoxDecoration(
                          color: isDark ? AppTheme.cardDark : Colors.white,
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(
                            color: isDark ? Colors.grey.shade800 : Colors.grey.shade300,
                          ),
                        ),
                        child: Row(
                          textDirection: TextDirection.rtl,
                          children: [
                            Icon(Icons.circle, size: 14, color: Theme.of(context).primaryColor),
                            const SizedBox(width: 16),
                            Text(
                              hadiths[index].hadithNumber,
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: Theme.of(context).primaryColor,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  Text(
                                    settings.titleLanguage == 'English'
                                        ? (chapterAsync.value?.titleEnglish ?? 'Hadith')
                                        : settings.titleLanguage == 'Arabic'
                                        ? (chapterAsync.value?.titleArabic ?? 'حديث')
                                        : (chapterAsync.value?.titleUrdu ?? 'حدیث'),
                                    textAlign: settings.titleLanguage == 'English' ? TextAlign.left : TextAlign.right,
                                    textDirection: settings.titleLanguage == 'English' ? TextDirection.ltr : TextDirection.rtl,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: AppTheme.safeGetFont(
                                      settings.titleLanguage == 'English'
                                          ? settings.englishFontFamily
                                          : settings.titleLanguage == 'Arabic'
                                          ? settings.arabicFontFamily
                                          : settings.urduFontFamily,
                                      color: Theme.of(context).primaryColor,
                                      fontSize: settings.titleLanguage == 'English'
                                          ? settings.englishFontSize
                                          : settings.titleLanguage == 'Arabic'
                                          ? settings.arabicFontSize
                                          : settings.urduFontSize,
                                      fontWeight: FontWeight.bold,
                                      height: 2.6,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    hadiths[index].urduText.replaceAll('\n', ' '),
                                    textAlign: TextAlign.right,
                                    textDirection: TextDirection.rtl,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: AppTheme.safeGetFont(
                                      settings.urduFontFamily,
                                      color: isDark ? Colors.white70 : Colors.black87,
                                      fontSize: (settings.urduFontSize * 0.8).clamp(12.0, 24.0),
                                      height: 2.4,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ).animate().fade(duration: 400.ms).slideY(begin: 0.1, end: 0, curve: Curves.easeOut, delay: (index * 50).ms);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
  // ── Find Dialog (AppBar icon) ─────────────────────────────────────────────
  void _showFindDialog(BuildContext context, int chapterId) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('حدیث نمبر سے جائیں'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'عالمی حدیث نمبر درج کریں',
              style: TextStyle(fontSize: 13, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                hintText: 'مثلاً: 1234',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.tag),
              ),
              autofocus: true,
              onSubmitted: (_) {
                Navigator.pop(ctx);
                _jumpByNumber(context, controller.text, chapterId);
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              _jumpByNumber(context, controller.text, chapterId);
            },
            child: const Text('Go'),
          ),
        ],
      ),
    );
  }

  // ── Jump by hadith_number (NOT chapter index) ────────────────────────────
  void _jumpByNumber(BuildContext context, String number, int currentChapterId) async {
    final numStr = number.trim();
    if (numStr.isEmpty) return;

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Row(
            children: [
              SizedBox(
                width: 18, height: 18,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              ),
              SizedBox(width: 12),
              Text('تلاش جاری ہے...'),
            ],
          ),
          duration: Duration(seconds: 3),
        ),
      );
    }

    try {
      final repo = ref.read(hadithRepositoryProvider);

      // Look up globally by hadith_number field (not list index)
      final hadith = await repo.getHadithByGlobalNumber(numStr);

      if (!context.mounted) return;
      ScaffoldMessenger.of(context).hideCurrentSnackBar();

      if (hadith == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('حدیث نمبر $numStr نہیں ملی'),
            backgroundColor: Colors.red.shade700,
          ),
        );
        return;
      }

      // Use the actual hadith.hadithNumber (not user input) for precise index lookup
      final index = await repo.getHadithIndex(hadith.chapterId, hadith.hadithNumber);

      if (!context.mounted) return;

      if (hadith.chapterId == currentChapterId) {
        context.pushReplacement('/home/chapter/${hadith.chapterId}?startIndex=$index');
      } else {
        context.push('/home/chapter/${hadith.chapterId}?startIndex=$index');
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خرابی: $e'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }
}
