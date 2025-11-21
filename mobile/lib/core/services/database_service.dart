import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  static Database? _database;

  DatabaseService._internal();

  factory DatabaseService() {
    return _instance;
  }

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, 'colegio_app.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createTables,
    );
  }

  Future<void> _createTables(Database db, int version) async {
    // Tabla de notificaciones recibidas
    await db.execute('''
      CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        notification_id TEXT UNIQUE,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        sender TEXT,
        sent_at TEXT NOT NULL,
        received_at TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        data TEXT
      )
    ''');

    // Tabla de notificaciones pendientes (sin enviar)
    await db.execute('''
      CREATE TABLE IF NOT EXISTS pending_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        recipient TEXT NOT NULL,
        created_at TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        retry_count INTEGER DEFAULT 0
      )
    ''');
  }

  // Métodos para notificaciones recibidas
  Future<int> insertNotification(Map<String, dynamic> notification) async {
    final db = await database;
    return await db.insert('notifications', notification);
  }

  Future<List<Map<String, dynamic>>> getAllNotifications() async {
    final db = await database;
    return await db.query(
      'notifications',
      orderBy: 'received_at DESC',
    );
  }

  Future<List<Map<String, dynamic>>> getUnreadNotifications() async {
    final db = await database;
    return await db.query(
      'notifications',
      where: 'is_read = ?',
      whereArgs: [0],
      orderBy: 'received_at DESC',
    );
  }

  Future<int> markNotificationAsRead(int id) async {
    final db = await database;
    return await db.update(
      'notifications',
      {'is_read': 1},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> deleteNotification(int id) async {
    final db = await database;
    return await db.delete(
      'notifications',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  // Métodos para notificaciones pendientes
  Future<int> insertPendingNotification(
      Map<String, dynamic> notification) async {
    final db = await database;
    return await db.insert('pending_notifications', notification);
  }

  Future<List<Map<String, dynamic>>> getPendingNotifications() async {
    final db = await database;
    return await db.query(
      'pending_notifications',
      where: 'status = ?',
      whereArgs: ['pending'],
    );
  }

  Future<int> updatePendingNotificationStatus(
      int id, String status) async {
    final db = await database;
    return await db.update(
      'pending_notifications',
      {'status': status},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> deletePendingNotification(int id) async {
    final db = await database;
    return await db.delete(
      'pending_notifications',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> close() async {
    final db = await database;
    await db.close();
  }
}
