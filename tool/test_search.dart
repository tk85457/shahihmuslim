import 'dart:io';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

void main() async {
  sqfliteFfiInit();
  var dbFactory = databaseFactoryFfi;
  final dbPath = 'assets/db/sahih_muslim.db';
  final db = await dbFactory.openDatabase(dbPath);

  final number = '1';

  final h = await db.rawQuery('SELECT * FROM hadiths WHERE TRIM(hadith_number) = ? LIMIT 1', [number]);
  if (h.isEmpty) {
    print('Hadith $number not found');
    exit(1);
  }
  
  final chapterId = h.first['chapter_id'];
  print('Found Hadith $number in Chapter $chapterId');

  final target = await db.rawQuery(
    'SELECT id FROM hadiths WHERE chapter_id = ? AND TRIM(hadith_number) = ? LIMIT 1',
    [chapterId, number]
  );
  
  if (target.isEmpty) {
    print('Failed second query');
  } else {
    final targetId = target.first['id'];
    print('Target ID: $targetId');

    final result = await db.rawQuery(
      'SELECT COUNT(*) as c FROM hadiths WHERE chapter_id = ? AND id < ?',
      [chapterId, targetId]
    );
    print('Index: ${result.first["c"]}');
  }

  await db.close();
  print('Done');
}
