import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';

class MannerTempWidget extends StatelessWidget {
  final double temp;
  const MannerTempWidget({super.key, required this.temp});

  Color get _color => AppColors.mannerTempColor(temp);

  @override
  Widget build(BuildContext context) {
    return Text(
      '🥕 ${temp.toStringAsFixed(1)}℃',
      style: TextStyle(
        color: _color,
        fontWeight: FontWeight.bold,
        fontSize: 18,
      ),
    );
  }
}
