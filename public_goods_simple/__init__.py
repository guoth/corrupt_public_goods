from otree.api import *



class C(BaseConstants):
    NAME_IN_URL = 'public_goods_simple'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 1
    ENDOWMENT = cu(100)
    MULTIPLIER = 1.8


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    # 被试编号字段
    subject_id = models.StringField(
        label="请输入您的被试编号："
    )
    # 简单问题答案字段
    comprehension_answer = models.IntegerField(
        label="1+1=几？"
    )
    # 原有的贡献字段
    contribution = models.CurrencyField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )


# FUNCTIONS
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
class ParticipantID(Page):
    """第一页：输入被试编号"""
    form_model = 'player'
    form_fields = ['subject_id']


class Instructions(Page):
    """第二页：实验背景介绍"""
    pass


class ComprehensionCheck(Page):
    """第三页：简单问题验证"""
    form_model = 'player'
    form_fields = ['comprehension_answer']
    
    def error_message(self, values):
        """验证答案是否正确"""
        if values['comprehension_answer'] != 2:
            return '答案不正确，请重新回答。'


class Contribute(Page):
    """第四页：公共品博弈环节"""
    form_model = 'player'
    form_fields = ['contribution']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


class ThankYou(Page):
    """最后一页：感谢页"""
    pass


page_sequence = [
    ParticipantID, 
    Instructions, 
    ComprehensionCheck, 
    Contribute, 
    ResultsWaitPage, 
    Results,
    ThankYou
]
