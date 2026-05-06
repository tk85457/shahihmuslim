import 'package:sqflite_common_ffi/sqflite_ffi.dart';

void main() async {
  sqfliteFfiInit();
  var dbFactory = databaseFactoryFfi;
  var db = await dbFactory.openDatabase('assets/sahih_muslim.db');

  final results = await db.query('chapters', limit: 1);
  print(results);
  final hadiths = await db.query('hadiths', limit: 1);
  print(hadiths.first.keys);

  await db.close();
}
