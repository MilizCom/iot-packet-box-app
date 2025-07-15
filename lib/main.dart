import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(MaterialApp(home: PaketBoxApp()));
}

class PaketBoxApp extends StatefulWidget {
  @override
  _PaketBoxAppState createState() => _PaketBoxAppState();
}

class _PaketBoxAppState extends State<PaketBoxApp> {
  final dbRef = FirebaseDatabase.instance.ref("box");
  bool paketAda = false;
  String status = "closed";

  @override
  void initState() {
    super.initState();
    dbRef.onValue.listen((event) {
      final data = Map<String, dynamic>.from(event.snapshot.value as dynamic);
      setState(() {
        paketAda = data['package'] ?? false;
        status = data['status'] ?? "closed";
      });
    });
  }

  void sendCommand(String cmd) {
    dbRef.child("command").set(cmd);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Smart Paket Box")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("Status Kunci: ${status == 'open' ? 'Terbuka 🔓' : 'Terkunci 🔐'}"),
            Text("Paket: ${paketAda ? 'ADA 📦' : 'TIDAK ADA 📭'}"),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: () => sendCommand("open"),
              child: Text("🔓 BUKA BOX"),
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: () => sendCommand("close"),
              child: Text("🔐 KUNCI BOX"),
            ),
          ],
        ),
      ),
    );
  }
}
