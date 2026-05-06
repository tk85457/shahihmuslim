import 'dart:io';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

void main() async {
  sqfliteFfiInit();
  final defaultFactory = databaseFactoryFfi;
  final dbPath = 'assets/db/sahih_muslim.db';
  final db = await defaultFactory.openDatabase(dbPath);

  final numStr = '8';

  // 1. Check getHadithByGlobalNumber
  List<Map<String, Object?>> hadiths = await db.query(
    'hadiths', 
    where: 'hadith_number = ?', 
    whereArgs: [numStr], 
    limit: 1
  );
  if (hadiths.isEmpty) {
    print('Failed to find Hadith $numStr globally with exact match.');
    hadiths = await db.rawQuery(
      'SELECT * FROM hadiths WHERE TRIM(hadith_number) = ? LIMIT 1', 
      [numStr.trim()]
    );
    if (hadiths.isEmpty) {
      print('Failed even with TRIM.');
      exit(1);
    }
  }

  final hadith = hadiths.first;
  final chapterId = hadith['chapter_id'] as int;
  print('Hadith $numStr found in chapter: $chapterId');

  // 2. Check getHadithIndex logic (which uses CAST)
  final count = await db.rawQuery(
    'SELECT COUNT(*) as c FROM hadiths WHERE chapter_id = ? AND CAST(hadith_number AS FLOAT) < CAST(? AS FLOAT)',
    [chapterId, numStr]
  );
  print('Result with CAST: Index is ${count.first['c']}');

  // Let's see what is actually at that index in that chapter
  final index = count.first['c'] as int;
  final atIndex = await db.query(
    'hadiths',
    where: 'chapter_id = ?',
    whereArgs: [chapterId],
    orderBy: 'id ASC',
    limit: 1,
    offset: index
  );
  if (atIndex.isNotEmpty) {
    print('Hadith opened at index $index is: ${atIndex.first['hadith_number']}');
  }

  await db.close();
}
