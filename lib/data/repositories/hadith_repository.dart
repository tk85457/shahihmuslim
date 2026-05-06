import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/models.dart';
import '../database/app_database.dart';
import 'search_query.dart';

final databaseProvider = Provider<AppDatabase>((ref) => AppDatabase.instance);

final hadithRepositoryProvider = Provider<HadithRepository>((ref) {
  return HadithRepository(ref.watch(databaseProvider));
});

final lastProgressProvider = FutureProvider<ReadingProgress?>((ref) async {
  final repo = ref.watch(hadithRepositoryProvider);
  return repo.getLastReadingProgress();
});

class HadithRepository {
  final AppDatabase _db;
  HadithRepository(this._db);

  // --- Chapters ---
  Future<List<Chapter>> getChapters() async {
    final db = await _db.database;
    final result = await db.query('chapters', orderBy: 'book_number ASC');
    return result.map((e) => Chapter.fromMap(e)).toList();
  }

  Future<int> getTotalChapterCount() async {
    final db = await _db.database;
    final result = await db.rawQuery('SELECT COUNT(*) as c FROM chapters');
    return result.first['c'] as int;
  }

  Future<Chapter?> getChapterById(int id) async {
    final db = await _db.database;
    final result = await db.query('chapters', where: 'id = ?', whereArgs: [id]);
    if (result.isEmpty) return null;
    return Chapter.fromMap(result.first);
  }

  // --- Hadiths (paginated) ---
  Future<List<Hadith>> getHadithsByChapter(
    int chapterId, {
    int? limit,
    int offset = 0,
  }) async {
    final db = await _db.database;

    // Step 1: Fetch primary hadiths for this page
    final primaryResults = await db.query(
      'hadiths',
      where: 'chapter_id = ? AND is_primary = 1',
      whereArgs: [chapterId],
      orderBy: 'id ASC',
      limit: limit,
      offset: offset,
    );

    if (primaryResults.isEmpty) return [];

    final primaryHadiths = primaryResults
        .map((e) => Hadith.fromMap(e))
        .toList();
    final primaryIds = primaryHadiths.map((h) => h.id).toList();

    // Step 2: Fetch ALL related chains for ALL primary hadiths on this page in ONE query
    final chainResults = await db.query(
      'hadiths',
      where: 'primary_hadith_id IN (${primaryIds.join(',')})',
      orderBy: 'id ASC',
    );

    // Step 3: Group chains by their primary_hadith_id
    final chainsMap = <int, List<Hadith>>{};
    for (var row in chainResults) {
      final h = Hadith.fromMap(row);
      if (h.primaryHadithId != null) {
        chainsMap.putIfAbsent(h.primaryHadithId!, () => []).add(h);
      }
    }

    // Step 4: Enrich primary hadiths with their chains
    return primaryHadiths.map((h) {
      return Hadith(
        id: h.id,
        chapterId: h.chapterId,
        hadithNumber: h.hadithNumber,
        arabicText: h.arabicText,
        urduText: h.urduText,
        englishText: h.englishText,
        isPrimary: h.isPrimary,
        primaryHadithId: h.primaryHadithId,
        relatedChains: chainsMap[h.id] ?? [],
      );
    }).toList();
  }

  Future<int> getHadithCountByChapter(int chapterId) async {
    final db = await _db.database;
    // Count only primary so UI pagination works perfectly
    final result = await db.rawQuery(
      'SELECT COUNT(*) as c FROM hadiths WHERE chapter_id = ? AND is_primary = 1',
      [chapterId],
    );
    return result.first['c'] as int;
  }

  Future<Hadith?> getHadithById(int id) async {
    final db = await _db.database;
    final result = await db.query('hadiths', where: 'id = ?', whereArgs: [id]);
    if (result.isEmpty) return null;
    return Hadith.fromMap(result.first);
  }

  Future<Hadith?> getHadithByNumber(String hadithNumber) async {
    final db = await _db.database;
    final result = await db.rawQuery(
      'SELECT * FROM hadiths WHERE TRIM(hadith_number) = ? LIMIT 1',
      [hadithNumber.trim()],
    );
    if (result.isEmpty) return null;
    return Hadith.fromMap(result.first);
  }

  Future<int> getHadithIndexWithinChapter(
    int chapterId,
    String hadithNumber,
  ) async {
    final db = await _db.database;
    final target = await db.rawQuery(
      'SELECT id, primary_hadith_id FROM hadiths WHERE chapter_id = ? AND TRIM(hadith_number) = ? LIMIT 1',
      [chapterId, hadithNumber.trim()],
    );
    if (target.isEmpty) return 0;

    // If the hadith is a secondary chain, jump to its primary parent
    int targetId = target.first['id'] as int;
    final primaryId = target.first['primary_hadith_id'] as int?;
    if (primaryId != null) {
      targetId = primaryId;
    }

    final result = await db.rawQuery(
      'SELECT COUNT(*) as c FROM hadiths WHERE chapter_id = ? AND is_primary = 1 AND id < ?',
      [chapterId, targetId],
    );
    return result.first['c'] as int;
  }

  Future<int> getTotalHadithCount() async {
    final db = await _db.database;
    final result = await db.rawQuery('SELECT COUNT(*) as c FROM hadiths');
    return result.first['c'] as int;
  }

  Future<Hadith?> getHadithByGlobalNumber(String number) async {
    final db = await _db.database;
    final trimmed = number.trim();

    // Step 1: Exact match on primary hadiths
    var result = await db.rawQuery(
      'SELECT * FROM hadiths WHERE TRIM(hadith_number) = ? AND is_primary = 1 LIMIT 1',
      [trimmed],
    );
    if (result.isNotEmpty) return Hadith.fromMap(result.first);

    // Step 2: Exact match on all hadiths (secondary chains too)
    result = await db.rawQuery(
      'SELECT * FROM hadiths WHERE TRIM(hadith_number) = ? LIMIT 1',
      [trimmed],
    );
    if (result.isNotEmpty) return Hadith.fromMap(result.first);

    // Step 3: Cast-based numeric comparison (handles '001', '1.0' formats)
    final numVal = int.tryParse(trimmed);
    if (numVal != null) {
      result = await db.rawQuery(
        'SELECT * FROM hadiths WHERE CAST(TRIM(hadith_number) AS INTEGER) = ? AND is_primary = 1 LIMIT 1',
        [numVal],
      );
      if (result.isNotEmpty) return Hadith.fromMap(result.first);
    }

    // Step 4: LIKE prefix match (e.g. user types '123', DB has '123a')
    result = await db.rawQuery(
      "SELECT * FROM hadiths WHERE TRIM(hadith_number) LIKE ? AND is_primary = 1 LIMIT 1",
      ['$trimmed%'],
    );
    if (result.isNotEmpty) return Hadith.fromMap(result.first);

    return null;
  }

  Future<int> getHadithIndex(int chapterId, String hadithNumber) async {
    final db = await _db.database;
    final target = await db.rawQuery(
      'SELECT id, primary_hadith_id FROM hadiths WHERE chapter_id = ? AND TRIM(hadith_number) = ? LIMIT 1',
      [chapterId, hadithNumber.trim()],
    );
    if (target.isEmpty) return 0;

    // If the searched hadith is a secondary chain, we should jump to its PRIMARY parent!
    int targetId = target.first['id'] as int;
    final primaryId = target.first['primary_hadith_id'] as int?;
    if (primaryId != null) {
      targetId = primaryId;
    }

    final result = await db.rawQuery(
      'SELECT COUNT(*) as c FROM hadiths WHERE chapter_id = ? AND is_primary = 1 AND id < ?',
      [chapterId, targetId],
    );
    return result.first['c'] as int;
  }

  // --- Search ---
  Future<List<Hadith>> searchHadiths(
    String query, {
    bool exactMatch = false,
    int limit = 30,
    int offset = 0,
  }) async {
    return _searchSqlite(
      query,
      exactMatch: exactMatch,
      limit: limit,
      offset: offset,
    );
  }

  Future<int> searchCount(String query, {bool exactMatch = false}) async {
    final db = await _db.database;
    final criteria = buildHadithSearchQuery(query, exactMatch: exactMatch);
    if (criteria == null) return 0;

    final result = await db.rawQuery(
      'SELECT COUNT(*) as c FROM hadiths WHERE ${criteria.where}',
      criteria.args,
    );
    return result.first['c'] as int;
  }

  // --- Bookmarks ---
  Future<List<Hadith>> getBookmarkedHadiths() async {
    final db = await _db.database;
    final result = await db.rawQuery('''
      SELECT h.* FROM hadiths h
      INNER JOIN bookmarks b ON h.id = b.hadith_id
      ORDER BY b.created_at DESC
    ''');
    return result.map((e) => Hadith.fromMap(e)).toList();
  }

  Future<void> toggleBookmark(int hadithId) async {
    final db = await _db.database;
    final exists = await db.query(
      'bookmarks',
      where: 'hadith_id = ?',
      whereArgs: [hadithId],
    );
    if (exists.isEmpty) {
      await db.insert('bookmarks', {
        'hadith_id': hadithId,
        'created_at': DateTime.now().toIso8601String(),
      });
    } else {
      await db.delete(
        'bookmarks',
        where: 'hadith_id = ?',
        whereArgs: [hadithId],
      );
    }
  }

  Future<bool> isBookmarked(int hadithId) async {
    final db = await _db.database;
    final r = await db.query(
      'bookmarks',
      where: 'hadith_id = ?',
      whereArgs: [hadithId],
    );
    return r.isNotEmpty;
  }

  // --- Collections ---
  Future<List<HadithCollection>> getCollections() async {
    final db = await _db.database;
    final result = await db.query('collections', orderBy: 'created_at DESC');
    return result.map((e) => HadithCollection.fromMap(e)).toList();
  }

  Future<int> createCollection(String name) async {
    final db = await _db.database;
    return await db.insert('collections', {
      'name': name,
      'created_at': DateTime.now().toIso8601String(),
    });
  }

  // --- Reading Progress ---
  Future<void> saveReadingProgress(int chapterId, int hadithIndex) async {
    final db = await _db.database;
    final now = DateTime.now().toIso8601String();
    final existing = await db.query(
      'reading_progress',
      where: 'chapter_id = ?',
      whereArgs: [chapterId],
    );
    if (existing.isEmpty) {
      await db.insert('reading_progress', {
        'chapter_id': chapterId,
        'hadith_index': hadithIndex,
        'last_read_at': now,
      });
    } else {
      await db.update(
        'reading_progress',
        {'hadith_index': hadithIndex, 'last_read_at': now},
        where: 'chapter_id = ?',
        whereArgs: [chapterId],
      );
    }
  }

  Future<ReadingProgress?> getLastReadingProgress() async {
    final db = await _db.database;
    final result = await db.query(
      'reading_progress',
      orderBy: 'last_read_at DESC',
      limit: 1,
    );
    if (result.isEmpty) return null;
    return ReadingProgress.fromMap(result.first);
  }

  // --- Stats ---
  Future<int> getBookmarkCount() async {
    final db = await _db.database;
    final r = await db.rawQuery('SELECT COUNT(*) as c FROM bookmarks');
    return r.first['c'] as int;
  }

  Future<int> getNotesCount() async {
    final db = await _db.database;
    final r = await db.rawQuery('SELECT COUNT(*) as c FROM notes');
    return r.first['c'] as int;
  }

  Future<int> getTotalReadChapters() async {
    final db = await _db.database;
    final r = await db.rawQuery(
      'SELECT COUNT(DISTINCT chapter_id) as c FROM reading_progress',
    );
    return r.first['c'] as int;
  }

  // --- Bookmarks with Chapter Info ---
  Future<List<Map<String, dynamic>>> getBookmarkedHadithsWithChapter() async {
    final db = await _db.database;
    final result = await db.rawQuery('''
      SELECT h.*, c.title_urdu as chapter_title_urdu, c.book_number
      FROM hadiths h
      INNER JOIN bookmarks b ON h.id = b.hadith_id
      LEFT JOIN chapters c ON h.chapter_id = c.id
      ORDER BY b.created_at DESC
    ''');
    return result;
  }

  // --- Notes ---
  Future<List<Map<String, dynamic>>> getNotesWithHadithInfo() async {
    final db = await _db.database;
    return await db.rawQuery('''
      SELECT n.*, h.hadith_number,
        SUBSTR(h.english_text, 1, 150) as hadith_preview
      FROM notes n
      LEFT JOIN hadiths h ON n.hadith_id = h.id
      ORDER BY n.updated_at DESC
    ''');
  }

  Future<void> addNote(int hadithId, String content) async {
    final db = await _db.database;
    final now = DateTime.now().toIso8601String();
    final existing = await db.query(
      'notes',
      where: 'hadith_id = ?',
      whereArgs: [hadithId],
    );
    if (existing.isEmpty) {
      await db.insert('notes', {
        'hadith_id': hadithId,
        'content': content,
        'created_at': now,
        'updated_at': now,
      });
    } else {
      await db.update(
        'notes',
        {'content': content, 'updated_at': now},
        where: 'hadith_id = ?',
        whereArgs: [hadithId],
      );
    }
  }

  Future<void> deleteNote(int noteId) async {
    final db = await _db.database;
    await db.delete('notes', where: 'id = ?', whereArgs: [noteId]);
  }

  // --- Collections ---
  Future<HadithCollection?> getCollectionById(int id) async {
    final db = await _db.database;
    final result = await db.query(
      'collections',
      where: 'id = ?',
      whereArgs: [id],
    );
    if (result.isEmpty) return null;
    return HadithCollection.fromMap(result.first);
  }

  Future<List<Hadith>> getCollectionHadiths(int collectionId) async {
    final db = await _db.database;
    final result = await db.rawQuery(
      '''
      SELECT h.* FROM hadiths h
      INNER JOIN collection_hadiths ch ON h.id = ch.hadith_id
      WHERE ch.collection_id = ?
    ''',
      [collectionId],
    );
    return result.map((e) => Hadith.fromMap(e)).toList();
  }

  Future<int> getCollectionHadithCount(int collectionId) async {
    final db = await _db.database;
    final r = await db.rawQuery(
      'SELECT COUNT(*) as c FROM collection_hadiths WHERE collection_id = ?',
      [collectionId],
    );
    return r.first['c'] as int;
  }

  Future<void> addHadithToCollection(int collectionId, int hadithId) async {
    final db = await _db.database;
    final existing = await db.query(
      'collection_hadiths',
      where: 'collection_id = ? AND hadith_id = ?',
      whereArgs: [collectionId, hadithId],
    );
    if (existing.isEmpty) {
      await db.insert('collection_hadiths', {
        'collection_id': collectionId,
        'hadith_id': hadithId,
      });
    }
  }

  Future<void> deleteCollection(int id) async {
    final db = await _db.database;
    await db.delete(
      'collection_hadiths',
      where: 'collection_id = ?',
      whereArgs: [id],
    );
    await db.delete('collections', where: 'id = ?', whereArgs: [id]);
  }

  // --- Hadith of the Day ---
  Future<Hadith?> getHadithOfTheDay() async {
    final db = await _db.database;
    // Use date-based index so it stays the same all day
    final now = DateTime.now();
    final dayOfYear = now.difference(DateTime(now.year, 1, 1)).inDays;
    final totalResult = await db.rawQuery('SELECT COUNT(*) as c FROM hadiths');
    final total = totalResult.first['c'] as int;
    if (total == 0) return null;
    final index = dayOfYear % total;
    final result = await db.rawQuery('SELECT * FROM hadiths LIMIT 1 OFFSET ?', [
      index,
    ]);
    if (result.isEmpty) return null;
    return Hadith.fromMap(result.first);
  }

  Future<Hadith?> getRandomHadith() async {
    final db = await _db.database;
    final result = await db.rawQuery(
      'SELECT * FROM hadiths ORDER BY RANDOM() LIMIT 1',
    );
    if (result.isEmpty) return null;
    return Hadith.fromMap(result.first);
  }

  // --- Chapter Progress ---
  Future<List<Map<String, dynamic>>> getAllChapterProgress() async {
    final db = await _db.database;
    return await db.rawQuery('''
      SELECT c.id, c.book_number, c.title_urdu, c.hadith_count,
        rp.hadith_index, rp.last_read_at
      FROM chapters c
      LEFT JOIN reading_progress rp ON c.id = rp.chapter_id
      ORDER BY c.book_number ASC
    ''');
  }

  // --- Export / Import ---
  Future<Map<String, dynamic>> exportUserData() async {
    final db = await _db.database;
    final bookmarks = await db.query('bookmarks');
    final notes = await db.query('notes');
    final collections = await db.query('collections');
    final collectionHadiths = await db.query('collection_hadiths');
    final progress = await db.query('reading_progress');
    return {
      'bookmarks': bookmarks,
      'notes': notes,
      'collections': collections,
      'collection_hadiths': collectionHadiths,
      'reading_progress': progress,
    };
  }

  Future<int> importUserData(Map<String, dynamic> data) async {
    final db = await _db.database;
    int count = 0;
    await db.transaction((txn) async {
      if (data['bookmarks'] != null) {
        for (final b in (data['bookmarks'] as List)) {
          try {
            await txn.insert('bookmarks', Map<String, dynamic>.from(b));
            count++;
          } catch (_) {}
        }
      }
      if (data['notes'] != null) {
        for (final n in (data['notes'] as List)) {
          try {
            await txn.insert('notes', Map<String, dynamic>.from(n));
            count++;
          } catch (_) {}
        }
      }
      if (data['collections'] != null) {
        for (final c in (data['collections'] as List)) {
          try {
            await txn.insert('collections', Map<String, dynamic>.from(c));
            count++;
          } catch (_) {}
        }
      }
      if (data['collection_hadiths'] != null) {
        for (final ch in (data['collection_hadiths'] as List)) {
          try {
            await txn.insert(
              'collection_hadiths',
              Map<String, dynamic>.from(ch),
            );
            count++;
          } catch (_) {}
        }
      }
      if (data['reading_progress'] != null) {
        for (final r in (data['reading_progress'] as List)) {
          try {
            await txn.insert('reading_progress', Map<String, dynamic>.from(r));
            count++;
          } catch (_) {}
        }
      }
    });
    return count;
  }

  // --- Reading Streak ---
  Future<void> recordReadingDay() async {
    final db = await _db.database;
    final today = DateTime.now().toIso8601String().substring(0, 10);
    await db.rawInsert(
      'INSERT OR REPLACE INTO reading_history (date, hadiths_read) VALUES (?, COALESCE((SELECT hadiths_read FROM reading_history WHERE date = ?), 0) + 1)',
      [today, today],
    );
  }

  Future<int> getReadingStreak() async {
    final db = await _db.database;
    final result = await db.rawQuery(
      'SELECT date FROM reading_history ORDER BY date DESC',
    );
    if (result.isEmpty) return 0;
    int streak = 0;
    DateTime checkDate = DateTime.now();
    for (final row in result) {
      final date = DateTime.parse(row['date'] as String);
      final checkString = checkDate.toIso8601String().substring(0, 10);
      final dateString = (row['date'] as String);
      if (dateString == checkString) {
        streak++;
        checkDate = checkDate.subtract(const Duration(days: 1));
      } else if (streak == 0 && checkDate.difference(date).inDays == 1) {
        // Allow today to not be recorded yet
        checkDate = checkDate.subtract(const Duration(days: 1));
        if (dateString == checkDate.toIso8601String().substring(0, 10)) {
          streak++;
          checkDate = checkDate.subtract(const Duration(days: 1));
        } else {
          break;
        }
      } else {
        break;
      }
    }
    return streak;
  }

  Future<int> getTotalDaysRead() async {
    final db = await _db.database;
    final result = await db.rawQuery(
      'SELECT COUNT(*) as c FROM reading_history',
    );
    return result.first['c'] as int;
  }

  // --- Search with language filter ---
  Future<List<Hadith>> searchByLanguage(
    String query, {
    String language = 'all',
    int limit = 30,
    int offset = 0,
  }) async {
    return _searchSqlite(
      query,
      language: language,
      limit: limit,
      offset: offset,
    );
  }

  Future<List<Hadith>> _searchSqlite(
    String query, {
    String language = 'all',
    bool exactMatch = false,
    int limit = 30,
    int offset = 0,
  }) async {
    final db = await _db.database;
    final criteria = buildHadithSearchQuery(
      query,
      language: language,
      exactMatch: exactMatch,
    );
    if (criteria == null) return [];

    final result = await db.rawQuery(
      'SELECT * FROM hadiths WHERE ${criteria.where} ORDER BY id ASC LIMIT ? OFFSET ?',
      [...criteria.args, limit, offset],
    );
    return result.map((e) => Hadith.fromMap(e)).toList();
  }
}
