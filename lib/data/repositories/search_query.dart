class HadithSearchQuery {
  final String where;
  final List<Object?> args;

  const HadithSearchQuery({required this.where, required this.args});
}

HadithSearchQuery? buildHadithSearchQuery(
  String query, {
  String language = 'all',
  bool exactMatch = false,
}) {
  final trimmed = query.trim();
  if (trimmed.isEmpty) return null;

  final textPattern = exactMatch ? trimmed : '%$trimmed%';

  switch (language) {
    case 'arabic':
      return HadithSearchQuery(
        where: '(arabic_text LIKE ? OR TRIM(hadith_number) = ?)',
        args: [textPattern, trimmed],
      );
    case 'urdu':
      return HadithSearchQuery(
        where: '(urdu_text LIKE ? OR TRIM(hadith_number) = ?)',
        args: [textPattern, trimmed],
      );
    case 'english':
      return HadithSearchQuery(
        where: '(english_text LIKE ? OR TRIM(hadith_number) = ?)',
        args: [textPattern, trimmed],
      );
    default:
      return HadithSearchQuery(
        where:
            '(urdu_text LIKE ? OR english_text LIKE ? OR arabic_text LIKE ? OR TRIM(hadith_number) = ?)',
        args: [textPattern, textPattern, textPattern, trimmed],
      );
  }
}
