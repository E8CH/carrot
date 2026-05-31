import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_endpoints.dart';
import '../../../core/providers/api_client_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../data/chats_repository.dart';
import 'chat_room_screen.dart';

class ChatListScreen extends ConsumerStatefulWidget {
  const ChatListScreen({super.key});

  @override
  ConsumerState<ChatListScreen> createState() => _ChatListScreenState();
}

class _ChatListScreenState extends ConsumerState<ChatListScreen> {
  List<Map<String, dynamic>> _rooms = [];
  bool _loading = true;
  String? _error;
  String? _myEmail;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    await _fetchMyEmail();
    await _loadRooms();
  }

  Future<void> _fetchMyEmail() async {
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.get(ApiEndpoints.usersMe);
      if (mounted) {
        _myEmail = (res as Map<String, dynamic>)['email'] as String?;
      }
    } catch (_) {}
  }

  Future<void> _loadRooms() async {
    try {
      final client = ref.read(apiClientProvider);
      final repo = ChatsRepository(client);
      final result = await repo.getChatRooms();
      if (!mounted) return;
      setState(() { _rooms = result; _loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() { _error = '채팅 목록을 불러올 수 없습니다.'; _loading = false; });
    }
  }

  String _formatElapsed(String isoString) {
    final diff = DateTime.now().difference(DateTime.parse(isoString));
    if (diff.inMinutes < 1) return '방금 전';
    if (diff.inMinutes < 60) return '${diff.inMinutes}분 전';
    if (diff.inHours < 24) return '${diff.inHours}시간 전';
    return '${diff.inDays}일 전';
  }

  void _openRoom(Map<String, dynamic> room) {
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => ChatRoomScreen(
        roomId: room['room_id'] as String,
        sellerEmail: room['seller_email'] as String,
        buyerEmail: room['buyer_email'] as String,
        myEmail: _myEmail ?? '',
        postId: room['post_id'] as int,
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('채팅', style: TextStyle(fontWeight: FontWeight.bold)),
        automaticallyImplyLeading: false,
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(child: Text(_error!, style: const TextStyle(color: Colors.red)));
    }
    if (_rooms.isEmpty) {
      return const Center(
        child: Text('채팅 내역이 없습니다.', style: TextStyle(color: Colors.grey)),
      );
    }
    return RefreshIndicator(
      onRefresh: _loadRooms,
      child: ListView.builder(
        itemCount: _rooms.length,
        itemBuilder: (ctx, i) => _buildTile(_rooms[i]),
      ),
    );
  }

  Widget _buildTile(Map<String, dynamic> room) {
    final thumbnail = room['post_thumbnail'] as String?;
    final opponentEmail = room['opponent_email'] as String? ?? '';
    final lastMessage = room['last_message'] as String? ?? '';
    final lastSentAt = room['last_sent_at'] as String? ?? '';
    final unreadCount = room['unread_count'] as int? ?? 0;

    return InkWell(
      onTap: () => _openRoom(room),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            // 게시글 썸네일
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
                image: thumbnail != null
                    ? DecorationImage(
                        image: NetworkImage(thumbnail),
                        fit: BoxFit.cover,
                        onError: (_, __) {},
                      )
                    : null,
              ),
              child: thumbnail == null
                  ? const Icon(Icons.image_outlined, color: Colors.grey, size: 24)
                  : null,
            ),
            const SizedBox(width: 12),
            // 텍스트 영역
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          opponentEmail,
                          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (lastSentAt.isNotEmpty)
                        Text(
                          _formatElapsed(lastSentAt),
                          style: const TextStyle(fontSize: 11, color: Colors.grey),
                        ),
                    ],
                  ),
                  const SizedBox(height: 3),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          lastMessage,
                          style: const TextStyle(fontSize: 13, color: Colors.grey),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (unreadCount > 0)
                        Container(
                          margin: const EdgeInsets.only(left: 4),
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.primary,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            unreadCount > 99 ? '99+' : '$unreadCount',
                            style: const TextStyle(color: Colors.white, fontSize: 11),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
