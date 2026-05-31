import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers/api_client_provider.dart';
import '../../features/posts/data/posts_repository.dart';

class TradeCompleteSheet extends ConsumerStatefulWidget {
  final int postId;
  final void Function(String? targetEmail) onComplete;

  const TradeCompleteSheet({
    super.key,
    required this.postId,
    required this.onComplete,
  });

  @override
  ConsumerState<TradeCompleteSheet> createState() => _TradeCompleteSheetState();
}

class _TradeCompleteSheetState extends ConsumerState<TradeCompleteSheet> {
  List<String> _buyers = [];
  String? _selected;
  bool _loading = false;
  bool _animating = false;
  bool _done = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadBuyers();
  }

  Future<void> _loadBuyers() async {
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      final buyers = await repo.getPostBuyers(widget.postId);
      if (mounted) setState(() => _buyers = buyers);
    } catch (_) {
      if (mounted) setState(() => _error = '구매자 목록을 불러오지 못했습니다.');
    }
  }

  Future<void> _confirm() async {
    if (_selected == null || _loading || _animating || _done) return;
    final messenger = ScaffoldMessenger.of(context);
    if (mounted) setState(() => _loading = true);
    try {
      final client = ref.read(apiClientProvider);
      final repo = PostsRepository(client);
      await repo.completePost(widget.postId, _selected!);
      if (mounted) setState(() { _loading = false; _animating = true; });
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) setState(() { _animating = false; _done = true; });
    } catch (_) {
      if (mounted) {
        setState(() => _loading = false);
        messenger.showSnackBar(
          const SnackBar(content: Text('거래완료 처리에 실패했습니다.')),
        );
      }
    }
  }

  void _finish({bool writeReview = false}) {
    Navigator.pop(context);
    widget.onComplete(writeReview ? _selected : null);
  }

  @override
  Widget build(BuildContext context) {
    if (_animating) return _buildAnimating();
    if (_done) return _buildDone();
    return _buildSelect();
  }

  Widget _buildSelect() {
    return Padding(
      padding: EdgeInsets.only(
        left: 24,
        right: 24,
        top: 24,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '거래한 상대를 선택해 주세요',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 13)),
            ),
          if (_buyers.isEmpty && _error == null)
            const Text('채팅한 구매자가 없습니다.', style: TextStyle(color: Colors.grey)),
          ...(_buyers.map((email) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: InkWell(
                  onTap: () => setState(() => _selected = email),
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: _selected == email
                            ? const Color(0xFFFF7E36)
                            : Colors.grey.shade200,
                      ),
                      borderRadius: BorderRadius.circular(8),
                      color: _selected == email
                          ? const Color(0xFFFFF3EE)
                          : Colors.white,
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            email,
                            style: TextStyle(
                              fontSize: 14,
                              color: _selected == email
                                  ? const Color(0xFFFF7E36)
                                  : Colors.black87,
                            ),
                          ),
                        ),
                        if (_selected == email)
                          const Icon(Icons.check, color: Color(0xFFFF7E36), size: 18),
                      ],
                    ),
                  ),
                ),
              ))),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('취소'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton(
                  onPressed: (_selected != null && !_loading) ? _confirm : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFFF7E36),
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: Colors.grey.shade300,
                  ),
                  child: Text(_loading ? '처리 중...' : '거래완료 확정'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAnimating() {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 48, horizontal: 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('✅', style: TextStyle(fontSize: 64)),
          SizedBox(height: 16),
          Text(
            '거래가 완료됐어요!',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildDone() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('✅', style: TextStyle(fontSize: 64)),
          const SizedBox(height: 12),
          const Text(
            '거래가 완료됐어요!',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            '상대방에게 후기를 남겨 매너온도를 올려보세요.',
            style: TextStyle(color: Colors.grey, fontSize: 13),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => _finish(writeReview: true),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFFF7E36),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text('후기 작성하기'),
            ),
          ),
          TextButton(
            onPressed: () => _finish(writeReview: false),
            child: const Text('나중에 하기', style: TextStyle(color: Colors.grey)),
          ),
        ],
      ),
    );
  }
}
