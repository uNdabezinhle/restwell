import 'package:flutter_test/flutter_test.dart';
import 'package:restwell_client_app/main.dart';

void main() {
  testWidgets('shows client app shell', (tester) async {
    await tester.pumpWidget(const RestWellClientApp());

    expect(find.text('Family services'), findsOneWidget);
    expect(find.text('Policies'), findsOneWidget);
  });
}
