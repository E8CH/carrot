import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/api_client_provider.dart';
import '../data/reviews_repository.dart';

class ReviewFormScreen extends ConsumerStatefulWidget {
  final int postId;
  final String targetEmail;
  const ReviewFormScreen({super.key, required this.postId, required this.targetEmail});
  @override
  ConsumerState<ReviewFormScreen> createState() => _ReviewFormScreenState();
}

class _ReviewFormScreenState extends ConsumerState<ReviewFormScreen> {
  static const List<String> _positiveTags = ['시간 약속을 잘 지켜요', '친절하고 매너 있어요', '물건 상태가 설명과 같아요', '거래 후 연락도 잘 돼요'];
  static const List<String> _negativeTags = ['시간 약속을 안 지켜요', '불친절했어요', '물건 상태가 설명과 달라요', '연락이 잘 안 돼요'];

  bool? _isPositive;
  final List<String> _selectedTags = [];
  final _commentCtrl = TextEditingController();
  bool _submitting = false;
  String? _error;

  @override
  void dispose() { _commentCtrl.dispose(); super.dispose(); }

  List<String> get _currentTags =>
      _isPositive == true ? _positiveTags : _isPositive == false ? _negativeTags : const [];

  void _setSentiment(bool positive) => setState(() { _isPositive = positive; _selectedTags.clear(); });

  void _toggleTag(String tag) => setState(() {
    _selectedTags.contains(tag) ? _selectedTags.remove(tag) : _selectedTags.add(tag);
  });

  Future<void> _submit() async {
    if (_isPositive == null || _submitting) return;
    final messenger = ScaffoldMessenger.of(context);
    final nav = Navigator.of(context);
    setState(() { _submitting = true; _error = null; });
    try {
      final client = ref.read(apiClientProvider);
      final repo = ReviewsRepository(client);
      await repo.submitReview(
        postId: widget.postId,
        isPositive: _isPositive!,
        tags: List.from(_selectedTags),
        comment: _commentCtrl.text.trim().isEmpty ? null : _commentCtrl.text.trim(),
      );
      messenger.showSnackBar(const SnackBar(content: Text('후기가 등록됐어요!'), backgroundColor: Color(0xFFFF7E36)));
      nav.pop();
    } catch (_) {
      if (mounted) setState(() { _error = '후기 작성에 실패했습니다.'; _submitting = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('후기 작성'), leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.of(context).pop())),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('거래 상대', style: TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 4),
          Text(widget.targetEmail, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
          const SizedBox(height: 24),
          const Text('거래는 어떠셨나요?', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: _SentimentButton(label: '좋았어요', selected: _isPositive == true, selectedColor: const Color(0xFFFF7E36), onTap: () => _setSentiment(true))),
            const SizedBox(width: 12),
            Expanded(child: _SentimentButton(label: '별로였어요', selected: _isPositive == false, selectedColor: Colors.blue, onTap: () => _setSentiment(false))),
          ]),
          if (_currentTags.isNotEmpty) ...[
            const SizedBox(height: 24),
            const Text('어떤 점이었나요?', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            Wrap(spacing: 8, runSpacing: 8, children: _currentTags.map((tag) => FilterChip(
              label: Text(tag, style: const TextStyle(fontSize: 13)),
              selected: _selectedTags.contains(tag),
              onSelected: (_) => _toggleTag(tag),
              selectedColor: const Color(0xFFFFF3EE),
              checkmarkColor: const Color(0xFFFF7E36),
              side: BorderSide(color: _selectedTags.contains(tag) ? const Color(0xFFFF7E36) : Colors.grey),
            )).toList()),
          ],
          const SizedBox(height: 24),
          const Text('한 줄 후기 (선택)', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          TextField(controller: _commentCtrl, maxLength: 500, maxLines: 3,
            decoration: InputDecoration(hintText: '상대방에 대한 후기를 남겨 주세요.', hintStyle: const TextStyle(color: Colors.grey),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFFFF7E36))))),
          if (_error != null) ...[const SizedBox(height: 8), Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 13))],
          const SizedBox(height: 100),
        ]),
      ),
      bottomNavigationBar: Padding(
        padding: EdgeInsets.only(left: 16, right: 16, bottom: MediaQuery.of(context).viewInsets.bottom + 16),
        child: SizedBox(width: double.infinity, height: 52, child: ElevatedButton(
          onPressed: (_isPositive != null && !_submitting) ? _submit : null,
          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFFF7E36), foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
          child: Text(_submitting ? '제출 중...' : '후기 제출하기', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        )),
      ),
    );
  }
}

class _SentimentButton extends StatelessWidget {
  final String label; final bool selected; final Color selectedColor; final VoidCallback onTap;
  const _SentimentButton({required this.label, required this.selected, required this.selectedColor, required this.onTap});
  @override
  Widget build(BuildContext context) {
    return GestureDetector(onTap: onTap, child: Container(
      padding: const EdgeInsets.symmetric(vertical: 14),
      decoration: BoxDecoration(
        border: Border.all(color: selected ? selectedColor : Colors.grey.shade300, width: selected ? 2 : 1),
        borderRadius: BorderRadius.circular(12),
        color: selected ? selectedColor.withValues(alpha: 0.08) : Colors.white,
      ),
      alignment: Alignment.center,
      child: Text(label, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: selected ? selectedColor : Colors.grey)),
    ));
  }
}
