from os import environ
import dj_database_url

# ================== 基本实验配置 ==================
SESSION_CONFIGS = [
    dict(
        name='public_goods_corrupt',
        display_name="公共品博弈实验（腐败组）",
        app_sequence=['public_goods_corrupt'],  # 你的实验 app 名
        num_demo_participants=4,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=3.00,  # 固定参与费3元
    doc="公共品博弈实验"
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ================== 国际化设置 ==================
LANGUAGE_CODE = 'zh-hans'
REAL_WORLD_CURRENCY_CODE = 'CNY'
USE_POINTS = True

# ================== 房间配置 ==================
ROOMS = [
    dict(
        name='experiment_room',
        display_name='实验房间',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(
        name='live_demo',
        display_name='实时演示（无参与者标签）'
    ),
]

# ================== 管理页面 ==================
ADMIN_USERNAME = 'admin'
# ✅ 推荐在 Render 环境变量中设置 OTREE_ADMIN_PASSWORD
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', '1234')  # 默认密码方便本地测试

# ================== 实验首页 ==================
DEMO_PAGE_INTRO_HTML = """
欢迎参加公共品博弈实验！
"""

# ================== 安全密钥 ==================
# ✅ 渲染部署时自动从环境变量读取，防止泄露
SECRET_KEY = environ.get('SECRET_KEY', 'default-unsafe-secret-key')

# ================== 应用加载 ==================
INSTALLED_APPS = ['otree']

# ================== 数据库配置 ==================
# ✅ Render 上自动使用 PostgreSQL，本地运行则默认 SQLite
DATABASES = {
    'default': dj_database_url.config(
        default=environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    )
}

# ================== 生产模式（隐藏 debug 信息） ==================
# ✅ 在 Render 环境变量中设置 OTREE_PRODUCTION=1 即可隐藏调试信息
if environ.get('OTREE_PRODUCTION'):
    DEBUG = False
else:
    DEBUG = True
