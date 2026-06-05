from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BrandViewSet, StoreViewSet, TeamViewSet, StreamRoomViewSet,
    EmployeeViewSet, ShiftViewSet, ScheduleViewSet,
    AttendanceViewSet, LeaveRequestViewSet,
    LiveSessionViewSet, ProductSalesViewSet,
    KPIConfigViewSet, PerformanceReviewViewSet, DashboardView
)
from .ai_views import AIViewSet
from .views_extra import (
    ProductCategoryViewSet, ProductViewSet, InventoryAlertViewSet,
    StreamScriptViewSet, ScriptSegmentViewSet, SalesScriptViewSet, StreamReviewViewSet,
    TaskBoardViewSet, TaskCardViewSet, NotificationViewSet,
    FinanceRecordViewSet, CommissionRuleViewSet, CommissionRecordViewSet,
    ContractViewSet, TrainingCourseViewSet, TrainingRecordViewSet,
    CompetitorViewSet, CompetitorDataViewSet, FanAnalysisViewSet,
    CampaignViewSet, GoalViewSet, OperationLogViewSet, BillboardConfigViewSet,
    RoleViewSet, UserRoleViewSet, KOLContactViewSet, ExportTaskViewSet,
)
from .views_extra2 import (
    StreamAlertViewSet, AssetViewSet, KnowledgeDocumentViewSet,
    ExpenseClaimViewSet, CustomerComplaintViewSet, StreamPlanViewSet,
    GiftRecordViewSet, FanGroupViewSet, DataReportViewSet, SupplierViewSet,
)
from .views_extra3 import (
    ProductSelectionViewSet, SampleViewSet, AdCampaignViewSet,
    ShortVideoViewSet, ComplianceReviewViewSet, PublicOpinionViewSet,
    AfterSalesOrderViewSet, RevenueSharingViewSet, BrandProjectViewSet,
    StreamSceneViewSet,
)
from .views_extra4 import (
    LiveInteractionViewSet, CouponViewSet, FlashSaleViewSet,
    RoomDecorationViewSet, ScriptTagViewSet,
    SignContractViewSet, BusinessNegotiationViewSet, InvestmentViewSet,
    ContractLedgerViewSet, AuthorizationViewSet,
    CompetitorRoomViewSet, TrafficAnalysisViewSet, UserPersonaViewSet,
    ABTestViewSet, DataWarningViewSet,
    SettlementViewSet, LogisticsViewSet, InventoryViewSet,
    ReturnAnalysisViewSet, TaxRecordViewSet,
)

router = DefaultRouter()
# 原有
router.register(r'brands', BrandViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'rooms', StreamRoomViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'shifts', ShiftViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'leaves', LeaveRequestViewSet)
router.register(r'sessions', LiveSessionViewSet)
router.register(r'product-sales', ProductSalesViewSet)
router.register(r'kpi-configs', KPIConfigViewSet)
router.register(r'reviews', PerformanceReviewViewSet)
router.register(r'dashboard', DashboardView, basename='dashboard')
# AI
router.register(r'ai', AIViewSet, basename='ai')
# 新增 20 功能
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'inventory-alerts', InventoryAlertViewSet)
router.register(r'stream-scripts', StreamScriptViewSet)
router.register(r'script-segments', ScriptSegmentViewSet)
router.register(r'sales-scripts', SalesScriptViewSet)
router.register(r'stream-reviews', StreamReviewViewSet)
router.register(r'task-boards', TaskBoardViewSet)
router.register(r'task-cards', TaskCardViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'finance', FinanceRecordViewSet)
router.register(r'commission-rules', CommissionRuleViewSet)
router.register(r'commissions', CommissionRecordViewSet)
router.register(r'contracts', ContractViewSet)
router.register(r'training-courses', TrainingCourseViewSet)
router.register(r'training-records', TrainingRecordViewSet)
router.register(r'competitors', CompetitorViewSet)
router.register(r'competitor-data', CompetitorDataViewSet)
router.register(r'fan-analysis', FanAnalysisViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'goals', GoalViewSet)
router.register(r'operation-logs', OperationLogViewSet)
router.register(r'billboard', BillboardConfigViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'kols', KOLContactViewSet)
router.register(r'exports', ExportTaskViewSet)
# 新增 10 功能
router.register(r'stream-alerts', StreamAlertViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'knowledge', KnowledgeDocumentViewSet)
router.register(r'expenses', ExpenseClaimViewSet)
router.register(r'complaints', CustomerComplaintViewSet)
router.register(r'stream-plans', StreamPlanViewSet)
router.register(r'gifts', GiftRecordViewSet)
router.register(r'fan-groups', FanGroupViewSet)
router.register(r'reports', DataReportViewSet)
router.register(r'suppliers', SupplierViewSet)
# 新增 10 业务功能
router.register(r'selections', ProductSelectionViewSet)
router.register(r'samples', SampleViewSet)
router.register(r'ad-campaigns', AdCampaignViewSet)
router.register(r'short-videos', ShortVideoViewSet)
router.register(r'compliance', ComplianceReviewViewSet)
router.register(r'opinions', PublicOpinionViewSet)
router.register(r'after-sales', AfterSalesOrderViewSet)
router.register(r'revenue-sharing', RevenueSharingViewSet)
router.register(r'brand-projects', BrandProjectViewSet)
router.register(r'scenes', StreamSceneViewSet)
# 新增 20 功能 (第四轮)
router.register(r'live-interactions', LiveInteractionViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'flash-sales', FlashSaleViewSet)
router.register(r'room-decorations', RoomDecorationViewSet)
router.register(r'script-tags', ScriptTagViewSet)
router.register(r'sign-contracts', SignContractViewSet)
router.register(r'negotiations', BusinessNegotiationViewSet)
router.register(r'investments', InvestmentViewSet)
router.register(r'contract-ledger', ContractLedgerViewSet)
router.register(r'authorizations', AuthorizationViewSet)
router.register(r'competitor-rooms', CompetitorRoomViewSet)
router.register(r'traffic-analysis', TrafficAnalysisViewSet)
router.register(r'user-personas', UserPersonaViewSet)
router.register(r'ab-tests', ABTestViewSet)
router.register(r'data-warnings', DataWarningViewSet)
router.register(r'settlements', SettlementViewSet)
router.register(r'logistics', LogisticsViewSet)
router.register(r'inventories', InventoryViewSet)
router.register(r'return-analysis', ReturnAnalysisViewSet)
router.register(r'tax-records', TaxRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
