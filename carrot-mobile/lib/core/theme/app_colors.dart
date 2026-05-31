import 'package:flutter/material.dart';

class AppColors {
  static const primary = Color(0xFFFF7E36);        // carrot 오렌지
  static const primaryHover = Color(0xFFE86D28);

  // 매너온도 색상 (UX-DR1, FR-18)
  static const mannerCold = Color(0xFF3B82F6);     // 0~30℃
  static const mannerWarm = Color(0xFFFF7E36);     // 36.5~50℃
  static const mannerHot = Color(0xFFEF4444);      // 50~99℃

  // 게시글 상태 배지 (UX-DR4)
  static const statusReserved = Color(0xFF6B7280); // 예약중
  static const statusDone = Color(0xFF374151);     // 거래완료

  // 기타
  static const white = Color(0xFFFFFFFF);
  static const black = Color(0xFF000000);
  static const grey100 = Color(0xFFF3F4F6);
  static const grey200 = Color(0xFFE5E7EB);
  static const grey400 = Color(0xFF9CA3AF);
  static const grey600 = Color(0xFF4B5563);

  static Color mannerTempColor(double temp) {
    if (temp <= 30) return mannerCold;
    if (temp <= 50) return mannerWarm;
    return mannerHot;
  }
}
