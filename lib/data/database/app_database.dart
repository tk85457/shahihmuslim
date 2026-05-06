import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/services.dart' show rootBundle;
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

/// Production database with asset-copy-on-first-launch pattern.
/// Data tables (chapters, hadiths) come from the pre-built asset.
/// User tables (bookmarks, collections, notes, reading_progress) are created on open.
class AppDatabase {
  static final AppDatabase instance = AppDatabase._init();
  static Database? _database;
  static const String _dbName = 'sahih_muslim.db';
  static const int _dbVersion = 5;

  AppDatabase._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _openDatabase();
    return _database!;
  }

  Future<Database> _openDatabase() async {
    final dbPath = await _getDatabasePath();

    if (kIsWeb) {
      return _openWebDatabase();
    }

    final file = File(dbPath);
    if (!await file.exists()) {
      await _copyFromAssets(dbPath);
    }

    if (!await File(dbPath).exists()) {
      debugPrintError('WARNING: DB file missing after asset copy attempt. '
          'App will open with empty DB and create tables from scratch.');
    }

    return await openDatabase(
      dbPath,
      version: _dbVersion,
      onOpen: _onOpen,
      onUpgrade: _onUpgrade,
    );
  }

  Future<String> _getDatabasePath() async {
    if (kIsWeb) return _dbName;
    final dir = await getApplicationDocumentsDirectory();
    final dbDir = Directory(join(dir.path, 'databases'));
    if (!await dbDir.exists()) await dbDir.create(recursive: true);
    return join(dbDir.path, _dbName);
  }

  Future<void> _copyFromAssets(String targetPath) async {
    try {
      debugPrintError('Copying DB from assets to: $targetPath');
      final data = await rootBundle.load('assets/db/$_dbName');
      final bytes = data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
      await File(targetPath).writeAsBytes(bytes, flush: true);
      debugPrintError('DB copy successful (${bytes.length} bytes).');
    } catch (e, stack) {
      debugPrintError('ERROR: Failed to copy DB from assets: $e\n$stack');
    }
  }

  /// Returns true if the core data table (hadiths) exists.
  Future<bool> _dataTablesExist(Database db) async {
    final result = await db.rawQuery(
      "SELECT name FROM sqlite_master WHERE type='table' AND name='hadiths'",
    );
    return result.isNotEmpty;
  }

  Future<Database> _openWebDatabase() async {
    const webDbName = 'sahih_muslim_web_v1.db';
    bool exists = await databaseFactory.databaseExists(webDbName);
    if (!exists) {
      debugPrintError('Web database not found. Copying from assets...');
      try {
        final data = await rootBundle.load('assets/db/$_dbName');
        final bytes = data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
        await databaseFactory.writeDatabaseBytes(webDbName, bytes);
        debugPrintError('Web database successfully copied from assets.');
      } catch (e) {
        debugPrintError('Failed to copy Web DB from assets: $e');
        return await openDatabase(
          webDbName,
          version: _dbVersion,
          onCreate: _createWebFallback,
          onOpen: _onOpen,
          onUpgrade: _onUpgrade,
        );
      }
    }
    return await openDatabase(
      webDbName,
      version: _dbVersion,
      onOpen: _onOpen,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _createWebFallback(Database db, int version) async {
    await _createDataTables(db);
    await _createUserTables(db);
    await _createIndexes(db);
  }

  /// FIX: Check data tables first. If asset copy failed and DB is empty,
  /// create data tables too — otherwise CREATE INDEX crashes on missing table.
  Future<void> _onOpen(Database db) async {
    final tablesExist = await _dataTablesExist(db);
    if (!tablesExist) {
      debugPrintError(
        'Data tables not found (asset copy may have failed). '
        'Creating schema from scratch.',
      );
      await _createDataTables(db);
    }
    await _createUserTables(db);
    await _createIndexes(db);
    await db.execute('PRAGMA foreign_keys = ON');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 5) {
      await _createUserTables(db);
      await _createIndexes(db);
    }
  }

  /// Fallback schema — must match the asset DB schema exactly so queries work
  /// even when the asset copy fails and tables are created from scratch.
  Future<void> _createDataTables(Database db) async {
    await db.execute('''
CREATE TABLE IF NOT EXISTS chapters (
  id INTEGER PRIMARY KEY,
  book_number INTEGER NOT NULL,
  title_arabic TEXT NOT NULL,
  title_urdu TEXT NOT NULL,
  title_english TEXT NOT NULL,
  hadith_count INTEGER NOT NULL DEFAULT 0
)''');

    await db.execute('''
CREATE TABLE IF NOT EXISTS hadiths (
  id INTEGER PRIMARY KEY,
  chapter_id INTEGER NOT NULL,
  hadith_number TEXT NOT NULL,
  arabic_text TEXT NOT NULL,
  urdu_text TEXT NOT NULL,
  english_text TEXT NOT NULL,
  is_primary INTEGER NOT NULL DEFAULT 1,
  primary_hadith_id INTEGER,
  FOREIGN KEY (chapter_id) REFERENCES chapters (id),
  FOREIGN KEY (primary_hadith_id) REFERENCES hadiths (id)
)''');
  }

  Future<void> _createUserTables(Database db) async {
    await db.execute('''
CREATE TABLE IF NOT EXISTS bookmarks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hadith_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (hadith_id) REFERENCES hadiths (id)
)''');

    await db.execute('''
CREATE TABLE IF NOT EXISTS collections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
)''');

    await db.execute('''
CREATE TABLE IF NOT EXISTS collection_hadiths (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  collection_id INTEGER NOT NULL,
  hadith_id INTEGER NOT NULL,
  FOREIGN KEY (collection_id) REFERENCES collections (id),
  FOREIGN KEY (hadith_id) REFERENCES hadiths (id),
  UNIQUE(collection_id, hadith_id)
)''');

    await db.execute('''
CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hadith_id INTEGER NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (hadith_id) REFERENCES hadiths (id)
)''');

    await db.execute('''
CREATE TABLE IF NOT EXISTS reading_progress (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chapter_id INTEGER NOT NULL,
  hadith_index INTEGER NOT NULL DEFAULT 0,
  last_read_at TEXT NOT NULL,
  FOREIGN KEY (chapter_id) REFERENCES chapters (id)
)''');

    await db.execute('''
CREATE TABLE IF NOT EXISTS reading_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL UNIQUE,
  hadiths_read INTEGER NOT NULL DEFAULT 1
)''');
  }

  Future<void> _createIndexes(Database db) async {
    await db.execute('CREATE INDEX IF NOT EXISTS idx_hadiths_chapter ON hadiths(chapter_id)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_hadiths_number ON hadiths(hadith_number)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_hadiths_primary ON hadiths(is_primary)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_hadith ON bookmarks(hadith_id)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_notes_hadith ON notes(hadith_id)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_progress_chapter ON reading_progress(chapter_id)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_collection_hadith ON collection_hadiths(collection_id)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_reading_history_date ON reading_history(date)');
  }

  /// Delete corrupted DB and re-copy from assets
  Future<void> resetDatabase() async {
    if (kIsWeb) return;
    final path = await _getDatabasePath();
    _database?.close();
    _database = null;
    final file = File(path);
    if (await file.exists()) await file.delete();
    _database = await _openDatabase();
  }

  Future<void> close() async {
    final db = await database;
    await db.close();
    _database = null;
  }
}

void debugPrintError(String msg) {
  // ignore: avoid_print
  assert(() { print('[AppDatabase] $msg'); return true; }());
}
