"""
Генератор текстовых отчетов для аналитики

Создает читаемый текст отчета из KPI данных
"""

from typing import Any

from src.config.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Генератор отчетов"""
    
    @staticmethod
    def generate_summary(kpi_data: dict[str, Any]) -> str:
        """
        Сгенерировать текстовый отчет из KPI данных
        
        Args:
            kpi_data: Словарь с KPI метриками
            
        Returns:
            Текст отчета
        """
        trend = kpi_data.get("trend", {})
        trend_emoji = trend.get("emoji", "➡️")
        trend_text = trend.get("text", "Стабильные продажи")
        
        # Формируем текст отчета
        summary_lines = [
            f"📊 <b>Анализ портфолио завершен!</b>",
            f"",
            f"📅 <b>Период:</b> {kpi_data.get('period', 'Не определен')}",
            f"📈 <b>Всего продаж:</b> {kpi_data.get('total_sales', 0)}",
            f"💰 <b>Общий доход:</b> ${kpi_data.get('total_revenue', 0):.2f}",
            f"",
            f"🎯 <b>Ключевые метрики:</b>",
            f"• CPM (доход на 1000 показов): ${kpi_data.get('cpm', 0):.2f}",
            f"• Коэффициент конверсии: {kpi_data.get('conversion_rate', 0):.2f}%",
            f"• Средний чек: ${kpi_data.get('average_check', 0):.2f}",
            f"",
        ]
        
        # Распределение по типам
        type_dist = kpi_data.get("type_distribution", {})
        if type_dist:
            summary_lines.append(f"📊 <b>Распределение по типам:</b>")
            for type_key, stats in type_dist.items():
                summary_lines.append(
                    f"• {type_key.capitalize()}: {stats['sales']} продаж, "
                    f"${stats['revenue']:.2f} доход"
                )
            summary_lines.append("")
        
        # Топ активов
        top_assets = kpi_data.get("top_assets", [])
        if top_assets:
            summary_lines.append(f"🔥 <b>Топ-{len(top_assets)} самых продаваемых:</b>")
            for i, asset in enumerate(top_assets, 1):
                title = asset.get("title", "Без названия")
                if len(title) > 50:
                    title = title[:47] + "..."
                summary_lines.append(
                    f"{i}. {title}: ${asset.get('revenue', 0):.2f} "
                    f"({asset.get('sales', 0)} продаж)"
                )
            summary_lines.append("")
        
        # Тренд
        summary_lines.extend([
            f"📈 <b>Тренд:</b> {trend_emoji} {trend_text}",
            f"",
        ])
        
        # Рекомендации
        recommendations = ReportGenerator._generate_recommendations(kpi_data)
        if recommendations:
            summary_lines.extend([
                f"💡 <b>Рекомендации:</b>",
                *[f"• {rec}" for rec in recommendations],
            ])
        
        return "\n".join(summary_lines)
    
    @staticmethod
    def _generate_recommendations(kpi_data: dict[str, Any]) -> list[str]:
        """
        Сгенерировать рекомендации на основе KPI
        
        Args:
            kpi_data: Словарь с KPI метриками
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        cpm = kpi_data.get("cpm", 0)
        conversion_rate = kpi_data.get("conversion_rate", 0)
        average_check = kpi_data.get("average_check", 0)
        trend = kpi_data.get("trend", {})
        trend_direction = trend.get("direction", "stable")
        
        # Рекомендации по CPM
        if cpm < 5:
            recommendations.append(
                "Низкий CPM. Попробуйте улучшить теги и описания активов для лучшей видимости"
            )
        elif cpm > 15:
            recommendations.append(
                "Отличный CPM! Продолжайте в том же духе"
            )
        
        # Рекомендации по конверсии
        if conversion_rate < 1:
            recommendations.append(
                "Низкая конверсия. Улучшите качество превью и оптимизируйте ключевые слова"
            )
        elif conversion_rate > 3:
            recommendations.append(
                "Высокая конверсия! Ваш контент востребован"
            )
        
        # Рекомендации по среднему чеку
        if average_check < 0.5:
            recommendations.append(
                "Низкий средний чек. Рассмотрите создание контента для премиум лицензий"
            )
        
        # Рекомендации по тренду
        if trend_direction == "declining":
            recommendations.append(
                "Продажи снижаются. Проанализируйте популярные категории и создайте больше контента в этих направлениях"
            )
        elif trend_direction == "growing":
            recommendations.append(
                "Отличный рост! Увеличьте количество активов в популярных категориях"
            )
        
        # Рекомендации по типам
        type_dist = kpi_data.get("type_distribution", {})
        if type_dist:
            best_category = max(
                type_dist.items(),
                key=lambda x: x[1].get("revenue", 0),
            )[0]
            recommendations.append(
                f"Больше всего дохода приносит категория '{best_category}'. "
                f"Создавайте больше контента в этом направлении"
            )
        
        return recommendations[:5]  # Максимум 5 рекомендаций

