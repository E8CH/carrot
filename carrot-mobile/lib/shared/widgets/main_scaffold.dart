import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers/api_client_provider.dart';
import '../../core/theme/app_colors.dart';
import '../../features/chatbot/presentation/chatbot_screen.dart';
import '../../features/chats/data/chats_repository.dart';
import '../../features/chats/presentation/chat_list_screen.dart';
import '../../features/my/presentation/my_screen.dart';
import '../../features/posts/presentation/feed_screen.dart';
import '../../features/posts/presentation/post_form_screen.dart';

class MainScaffold extends ConsumerStatefulWidget {
  const MainScaffold({super.key});

  @override
  ConsumerState<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends ConsumerState<MainScaffold> {
  int _selectedIndex = 0;
  int _unreadCount = 0;
  Timer? _unreadTimer;

  int _feedRefreshKey = 0;

  @override
  void initState() {
    super.initState();
    _pollUnreadCount();
    _unreadTimer = Timer.periodic(
      const Duration(milliseconds: 2500),
      (_) => _pollUnreadCount(),
    );
  }

  @override
  void dispose() {
    _unreadTimer?.cancel();
    super.dispose();
  }

  Future<void> _pollUnreadCount() async {
    try {
      final client = ref.read(apiClientProvider);
      final repo = ChatsRepository(client);
      final result = await repo.getUnreadCount();
      final count = result['count'] as int? ?? 0;
      if (mounted) setState(() => _unreadCount = count);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          FeedScreen(key: ValueKey(_feedRefreshKey)),
          const ChatListScreen(),
          const MyScreen(),
        ],
      ),
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (_selectedIndex == 0) ...[
            FloatingActionButton(
              heroTag: 'write',
              onPressed: () => Navigator.of(context)
                  .push(MaterialPageRoute(builder: (_) => const PostFormScreen()))
                  .then((_) => setState(() => _feedRefreshKey++)),
              backgroundColor: AppColors.primary,
              child: const Icon(Icons.add, color: Colors.white),
            ),
            const SizedBox(height: 10),
          ],
          FloatingActionButton.small(
            heroTag: 'chatbot',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const ChatBotScreen()),
            ),
            backgroundColor: Colors.white,
            elevation: 2,
            child: const Icon(Icons.support_agent, color: AppColors.primary),
          ),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (i) => setState(() => _selectedIndex = i),
        destinations: [
          const NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: '홈',
          ),
          NavigationDestination(
            icon: Badge(
              isLabelVisible: _unreadCount > 0,
              label: Text(
                _unreadCount > 99 ? '99+' : '$_unreadCount',
                style: const TextStyle(fontSize: 10),
              ),
              child: const Icon(Icons.chat_bubble_outline),
            ),
            selectedIcon: Badge(
              isLabelVisible: _unreadCount > 0,
              label: Text(
                _unreadCount > 99 ? '99+' : '$_unreadCount',
                style: const TextStyle(fontSize: 10),
              ),
              child: const Icon(Icons.chat_bubble),
            ),
            label: '채팅',
          ),
          const NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: '나의당근',
          ),
        ],
      ),
    );
  }
}
