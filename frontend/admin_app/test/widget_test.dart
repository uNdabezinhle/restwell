import 'package:flutter_test/flutter_test.dart';
import 'package:restwell_admin_app/main.dart';

void main() {
  testWidgets('shows admin login shell', (tester) async {
    await tester.pumpWidget(const RestWellAdminApp());

    expect(find.text('RestWell'), findsOneWidget);
    expect(find.text('Admin and staff workspace'), findsOneWidget);
  });

  testWidgets('validates login form input', (tester) async {
    await tester.pumpWidget(const RestWellAdminApp());

    await tester.tap(find.text('Sign in'));
    await tester.pump();

    expect(find.text('Enter your username.'), findsOneWidget);
    expect(find.text('Enter your password.'), findsOneWidget);
  });
}
