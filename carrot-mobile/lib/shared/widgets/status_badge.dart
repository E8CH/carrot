import 'package:flutter/material.dart';

class StatusBadge extends StatelessWidget {
  final String status;
  const StatusBadge({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    Color? bgColor;
    switch (status) {
      case '예약중':
        bgColor = const Color(0xFF6B7280);
      case '거래완료':
        bgColor = const Color(0xFF374151);
      default:
        return const SizedBox.shrink(); // 판매중은 배지 없음
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        status,
        style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w500),
      ),
    );
  }
}
