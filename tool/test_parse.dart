// ignore_for_file: avoid_print
import 'dart:convert';
import 'dart:io';

void main() async {
  final jsonFile = File(r'C:\Users\tk854\Music\Downloads\Sahih%20al-Bukhari.json');
  final txtFile = File(r'C:\Users\tk854\Music\Downloads\urdubukhari.txt');

  final content = await jsonFile.readAsString();
  final List<dynamic> jsonList = jsonDecode(content);

  print('JSON[0]:');
  final first = jsonList[0] as Map<String, dynamic>;
  first.forEach((k, v) => print('  $k: $v'));

  final txtLines = await txtFile.readAsLines();
  print('\nTXT[0]: ${txtLines[0]}');
  print('\nTXT[1]: ${txtLines[1]}');

  int maxChapter = 0;
  for (var item in jsonList) {
    int c = item['Chapter_Number'] as int;
    if (c > maxChapter) maxChapter = c;
  }
  print('\nMax Chapter_Number: $maxChapter');
}
