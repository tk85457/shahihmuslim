import 'dart:io';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

void main() async {
  sqfliteFfiInit();
  final databaseFactory = databaseFactoryFfi;
  final dbPath = 'assets/db/sahih_muslim.db';
  
  if (!File(dbPath).existsSync()) {
    print('DB not found: $dbPath');
    return;
  }

  final db = await databaseFactory.openDatabase(dbPath);
  final hadiths = await db.rawQuery('SELECT hadith_number FROM hadiths LIMIT 20');
  
  print('First 20 Hadith Numbers:');
  for (var h in hadiths) {
    print("'${h['hadith_number']}'");
  }

  final searchTests = ['1', '434', '5'];
  for (var st in searchTests) {
       final res = await db.rawQuery("SELECT hadith_number FROM hadiths WHERE hadith_number LIKE '%$st%' LIMIT 5");
       print('Matches for $st: $res');
  }

  await db.close();
}
