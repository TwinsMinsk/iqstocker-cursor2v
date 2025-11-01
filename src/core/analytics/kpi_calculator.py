"""
Калькулятор KPI метрик для анализа CSV

Расчет CPM, конверсии, трендов и других метрик
"""

from datetime import datetime, timedelta
from typing import Any

from src.config.logging import get_logger

logger = get_logger(__name__)


class KPICalculator:
    """Калькулятор KPI метрик"""
    
    @staticmethod
    def calculate_kpi(data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Рассчитать все KPI метрики из данных CSV
        
        Args:
            data: Список словарей с данными из CSV
            
        Returns:
            Словарь с KPI метриками
        """
        if not data:
            return KPICalculator._get_empty_kpi()
        
        # Базовые метрики
        total_sales = sum(1 for row in data if row.get("revenue", 0) > 0)
        total_revenue = sum(float(row.get("revenue", 0)) for row in data)
        total_impressions = sum(int(row.get("impressions", 0)) for row in data)
        total_downloads = sum(int(row.get("downloads", 0)) for row in data)
        
        # Расчет CPM
        if total_impressions > 0:
            cpm = (total_revenue / total_impressions) * 1000
        else:
            cpm = 0.0
        
        # Расчет конверсии
        if total_impressions > 0:
            conversion_rate = (total_sales / total_impressions) * 100
        else:
            conversion_rate = 0.0
        
        # Средний чек
        if total_sales > 0:
            average_check = total_revenue / total_sales
        else:
            average_check = 0.0
        
        # Тренд
        trend = KPICalculator._calculate_trend(data)
        
        # Топ активов
        top_assets = KPICalculator._get_top_assets(data, limit=3)
        
        # Распределение по типам
        type_distribution = KPICalculator._get_type_distribution(data)
        
        # Период анализа
        dates = [
            datetime.fromisoformat(row.get("date", ""))
            for row in data
            if row.get("date")
        ]
        
        if dates:
            period_start = min(dates).strftime("%Y-%m-%d")
            period_end = max(dates).strftime("%Y-%m-%d")
            period = f"{period_start} - {period_end}"
        else:
            period = "Не определен"
        
        return {
            "total_sales": total_sales,
            "total_revenue": round(total_revenue, 2),
            "total_impressions": total_impressions,
            "total_downloads": total_downloads,
            "cpm": round(cpm, 2),
            "conversion_rate": round(conversion_rate, 2),
            "average_check": round(average_check, 2),
            "trend": trend,
            "top_assets": top_assets,
            "type_distribution": type_distribution,
            "period": period,
            "period_start": period_start if dates else None,
            "period_end": period_end if dates else None,
            "row_count": len(data),
        }
    
    @staticmethod
    def _calculate_trend(data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Рассчитать тренд продаж
        
        Сравнивает последние 30 дней с предыдущим периодом
        
        Args:
            data: Список данных
            
        Returns:
            Словарь с информацией о тренде
        """
        if len(data) < 2:
            return {
                "direction": "stable",
                "emoji": "➡️",
                "text": "Недостаточно данных для анализа тренда",
                "change_percent": 0.0,
            }
        
        # Группируем по датам
        revenue_by_date: dict[str, float] = {}
        for row in data:
            date_str = row.get("date", "")
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str)
                    date_key = date_obj.strftime("%Y-%m-%d")
                    revenue_by_date[date_key] = revenue_by_date.get(date_key, 0) + float(row.get("revenue", 0))
                except (ValueError, AttributeError):
                    continue
        
        if len(revenue_by_date) < 2:
            return {
                "direction": "stable",
                "emoji": "➡️",
                "text": "Недостаточно данных для анализа тренда",
                "change_percent": 0.0,
            }
        
        # Сортируем по датам
        sorted_dates = sorted(revenue_by_date.keys())
        
        # Берем последние 30 дней и предыдущий период
        now = datetime.utcnow()
        last_30_days = [
            date for date in sorted_dates
            if datetime.strptime(date, "%Y-%m-%d") >= now - timedelta(days=30)
        ]
        previous_period = [
            date for date in sorted_dates
            if datetime.strptime(date, "%Y-%m-%d") < now - timedelta(days=30)
            and datetime.strptime(date, "%Y-%m-%d") >= now - timedelta(days=60)
        ]
        
        recent_revenue = sum(revenue_by_date[date] for date in last_30_days)
        previous_revenue = sum(revenue_by_date[date] for date in previous_period)
        
        if previous_revenue == 0:
            if recent_revenue > 0:
                return {
                    "direction": "growing",
                    "emoji": "📈",
                    "text": "Рост продаж!",
                    "change_percent": 100.0,
                }
            return {
                "direction": "stable",
                "emoji": "➡️",
                "text": "Стабильные продажи",
                "change_percent": 0.0,
            }
        
        change_percent = ((recent_revenue - previous_revenue) / previous_revenue) * 100
        
        if change_percent > 10:
            return {
                "direction": "growing",
                "emoji": "📈",
                "text": f"Рост продаж на {abs(change_percent):.1f}%",
                "change_percent": round(change_percent, 1),
            }
        elif change_percent < -10:
            return {
                "direction": "declining",
                "emoji": "📉",
                "text": f"Снижение продаж на {abs(change_percent):.1f}%",
                "change_percent": round(change_percent, 1),
            }
        else:
            return {
                "direction": "stable",
                "emoji": "➡️",
                "text": "Стабильные продажи",
                "change_percent": round(change_percent, 1),
            }
    
    @staticmethod
    def _get_top_assets(
        data: list[dict[str, Any]],
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Получить топ активов по доходу
        
        Args:
            data: Список данных
            limit: Количество топ активов
            
        Returns:
            Список топ активов
        """
        # Группируем по asset_id или title
        assets: dict[str, dict[str, Any]] = {}
        
        for row in data:
            asset_id = str(row.get("asset_id", ""))
            title = str(row.get("title", ""))
            revenue = float(row.get("revenue", 0))
            
            key = asset_id or title
            if key not in assets:
                assets[key] = {
                    "asset_id": asset_id,
                    "title": title[:50] if len(title) > 50 else title,  # Обрезаем длинные заголовки
                    "revenue": 0.0,
                    "sales": 0,
                }
            
            assets[key]["revenue"] += revenue
            if revenue > 0:
                assets[key]["sales"] += 1
        
        # Сортируем по revenue
        sorted_assets = sorted(
            assets.values(),
            key=lambda x: x["revenue"],
            reverse=True,
        )
        
        # Форматируем для отображения
        return [
            {
                "title": asset["title"],
                "revenue": round(asset["revenue"], 2),
                "sales": asset["sales"],
            }
            for asset in sorted_assets[:limit]
        ]
    
    @staticmethod
    def _get_type_distribution(
        data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Получить распределение по типам активов
        
        Args:
            data: Список данных
            
        Returns:
            Словарь с распределением
        """
        distribution: dict[str, dict[str, Any]] = {}
        
        for row in data:
            category = str(row.get("category", "unknown")).lower()
            purchase_type = str(row.get("purchase_type", "unknown")).lower()
            revenue = float(row.get("revenue", 0))
            
            # Используем category если есть, иначе purchase_type
            type_key = category if category != "unknown" else purchase_type
            
            if type_key not in distribution:
                distribution[type_key] = {
                    "count": 0,
                    "revenue": 0.0,
                    "sales": 0,
                }
            
            distribution[type_key]["count"] += 1
            distribution[type_key]["revenue"] += revenue
            if revenue > 0:
                distribution[type_key]["sales"] += 1
        
        # Форматируем
        formatted = {}
        for key, value in distribution.items():
            formatted[key] = {
                "count": value["count"],
                "revenue": round(value["revenue"], 2),
                "sales": value["sales"],
            }
        
        return formatted
    
    @staticmethod
    def _get_empty_kpi() -> dict[str, Any]:
        """Получить пустые KPI метрики"""
        return {
            "total_sales": 0,
            "total_revenue": 0.0,
            "total_impressions": 0,
            "total_downloads": 0,
            "cpm": 0.0,
            "conversion_rate": 0.0,
            "average_check": 0.0,
            "trend": {
                "direction": "stable",
                "emoji": "➡️",
                "text": "Нет данных",
                "change_percent": 0.0,
            },
            "top_assets": [],
            "type_distribution": {},
            "period": "Не определен",
            "period_start": None,
            "period_end": None,
            "row_count": 0,
        }

