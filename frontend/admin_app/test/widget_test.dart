import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:restwell_admin_app/main.dart';

void main() {
  testWidgets('shows admin login shell', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: RestWellAdminApp()));

    expect(find.text('RestWell'), findsOneWidget);
    expect(find.text('Admin and staff workspace'), findsOneWidget);
  });

  testWidgets('validates login form input', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: RestWellAdminApp()));

    await tester.tap(find.text('Sign in'));
    await tester.pump();

    expect(find.text('Enter your username.'), findsOneWidget);
    expect(find.text('Enter your password.'), findsOneWidget);
  });
}
