from otree.api import *



class C(BaseConstants):
    NAME_IN_URL = 'public_goods_control1'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 2
    ENDOWMENT = cu(20)
    MULTIPLIER = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    # 知情同意字段
    consent = models.BooleanField(
        label="我已阅读并同意参加本实验"
    )
    # 被试编号字段（限定为数字）
    subject_id = models.IntegerField(
        label="请输入您的被试编号："
    )
    # 玩家角色字段（A、B、C 或 D）
    player_role = models.StringField()
    # 理解检查问题1：公共池倍率（选择题，正确答案为2）
    comprehension_q1 = models.IntegerField(
        label="公共池的倍率为多少？",
        choices=[
            [1, 'A. 1'],
            [2, 'B. 2'],
            [3, 'C. 3'],
            [4, 'D. 4'],
        ],
        widget=widgets.RadioSelect
    )
    # 理解检查问题2：角色数量（选择题，正确答案为4）
    comprehension_q2 = models.IntegerField(
        label="每组中共有几种角色？",
        choices=[
            [1, 'A. 1'],
            [2, 'B. 2'],
            [3, 'C. 3'],
            [4, 'D. 4'],
        ],
        widget=widgets.RadioSelect
    )
    # 理解检查问题3：最终获得代币数（填空题，正确答案为20）
    comprehension_q3 = models.IntegerField(
        label='''假设你和另外3名组员每人一开始都有20个代币。每个人都向小组的“公共账户”投入了10个代币。请问：最后你手中总共会有多少代币？（只需填写数字）？<br>
        
        你的收益=你留下的代币数＋（包括你在内的所有成员投入公共池的代币总数x2）/4'''
    )
    # 原有的贡献字段
    contribution = models.CurrencyField(
        min=0, max=C.ENDOWMENT, label="你选择投入公共池的代币数为："
    )
    # 反应时字段（毫秒）：从看到投资决策页面到提交决策的时间
    reaction_time = models.FloatField(initial=0)
    # 页面加载时间戳
    page_load_time = models.FloatField(initial=0)
    
    @property
    def role(self):
        """返回玩家角色，用于模板显示"""
        return self.player_role


# FUNCTIONS
def creating_session(subsession: Subsession):
    """为每个玩家分配角色 A、B、C 或 D；第2轮沿用第1轮角色与分组"""
    import random
    roles = ['A', 'B', 'C', 'D']
    
    # 第2轮起保持与第1轮相同的分组（确保角色位置一致）
    if subsession.round_number > 1:
        subsession.group_like_round(1)
    
    for group in subsession.get_groups():
        players = group.get_players()
        
        if subsession.round_number == 1:
            # 第1轮：随机打乱并分配角色
            assigned_roles = roles.copy()
            random.shuffle(assigned_roles)
            for i, player in enumerate(players):
                player.player_role = assigned_roles[i]
                # 缓存玩家角色，供后续轮次继承
                player.participant.vars['player_role'] = player.player_role
        else:
            # 第2轮及以后：沿用玩家在第1轮的角色
            for player in players:
                stored_role = player.participant.vars.get('player_role')
                if stored_role:
                    player.player_role = stored_role
        
        # 跨轮次继承被试编号
        if subsession.round_number > 1:
            for player in players:
                stored_subject_id = player.participant.vars.get('subject_id')
                if stored_subject_id is not None:
                    player.subject_id = stored_subject_id


def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = (
        group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    )
    for p in players:
        p.payoff = C.ENDOWMENT - p.contribution + group.individual_share


# PAGES
class ConsentPage(Page):
    """知情同意页面：只在第一轮显示"""
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('consent'):
            return '您必须同意参加实验才能继续'


class ParticipantID(Page):
    """第一页：输入被试编号"""
    form_model = 'player'
    form_fields = ['subject_id']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['subject_id'] = player.subject_id


class Instructions(Page):
    """第二页：实验背景介绍"""
    pass


class ComprehensionCheck(Page):
    """第三页：理解检查"""
    form_model = 'player'
    form_fields = ['comprehension_q1', 'comprehension_q2', 'comprehension_q3']
    
    def error_message(self, values):
        """验证答案是否正确"""
        errors = []
        
        # 检查问题1：公共池倍率，正确答案为2
        if values.get('comprehension_q1') != 2:
            errors.append('问题1答案不正确，请重新回答。')
        
        # 检查问题2：角色数量，正确答案为4
        if values.get('comprehension_q2') != 4:
            errors.append('问题2答案不正确，请重新回答。')
        
        # 检查问题3：最终获得代币数，正确答案为30
        if values.get('comprehension_q3') != 30:
            errors.append('问题3答案不正确，请重新回答。')
        
        if errors:
            return ' '.join(errors)


class ComprehensionWaitPage(WaitPage):
    """理解检验后等待页面"""
    title_text = "等待其他玩家"
    body_text = "请稍候，等待其他玩家完成理解检验并加入正式实验..."


class MatchingWaitPage(Page):
    """匹配等待页面"""
    timeout_seconds = 4
    title_text = "正在匹配其他玩家"
    body_text = "请稍候，正在为您匹配其他玩家..."


class MatchingSuccess(Page):
    """匹配成功页面"""
    timeout_seconds = 4


class Contribute(Page):
    """第四页：公共品博弈环节"""
    form_model = 'player'
    form_fields = ['contribution', 'reaction_time', 'page_load_time']
    
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'player_role': player.role
        }


class ResultsWaitPage(WaitPage):
    title_text = "等待其他玩家"
    body_text = "请稍候，等待其他玩家完成决策..."
    after_all_players_arrive = set_payoffs


class Results(Page):
    """结果页面：显示感谢和截图提醒"""

    @staticmethod
    def vars_for_template(player: Player):
        stored_subject_id = player.field_maybe_none('subject_id')
        if stored_subject_id is None:
            stored_subject_id = player.participant.vars.get('subject_id')
            if stored_subject_id is not None:
                player.subject_id = stored_subject_id
        return dict(subject_id=stored_subject_id)


class ThankYou(Page):
    """最后一页：感谢页"""
    pass


page_sequence = [
    ConsentPage,
    ParticipantID, 
    Instructions, 
    ComprehensionCheck, 
    ComprehensionWaitPage,
    MatchingWaitPage,
    MatchingSuccess,
    Contribute, 
    ResultsWaitPage, 
    Results,
]
