import 'package:flutter_test/flutter_test.dart';
import 'package:shahihmuslim/data/repositories/search_query.dart';

void main() {
  group('buildHadithSearchQuery', () {
    test('returns null for empty search text', () {
      expect(buildHadithSearchQuery('   '), isNull);
    });

    test('keeps untrusted input in SQL arguments', () {
      const query = "faith%' OR 1=1 --";

      final criteria = buildHadithSearchQuery(query)!;

      expect(criteria.where, isNot(contains(query)));
      expect(criteria.args, contains("%$query%"));
      expect(criteria.args, contains(query));
    });

    test('limits language-specific search to the selected text column', () {
      final criteria = buildHadithSearchQuery('iman', language: 'urdu')!;

      expect(criteria.where, contains('urdu_text LIKE ?'));
      expect(criteria.where, isNot(contains('english_text LIKE ?')));
      expect(criteria.where, isNot(contains('arabic_text LIKE ?')));
      expect(criteria.args, ['%iman%', 'iman']);
    });
  });
}
