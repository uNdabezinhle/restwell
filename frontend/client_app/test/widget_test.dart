import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:restwell_client_app/main.dart';

void main() {
  testWidgets('shows client login shell', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: RestWellClientApp()));

    expect(find.text('RestWell'), findsOneWidget);
    expect(find.text('Family portal'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
  });
}
