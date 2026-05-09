class HEARTScorer:
    """HEART score: History + ECG + Age + Risk factors + Troponin"""

    MACE = {'Normal':'< 2%','Routine':'12-65%','Urgent':'> 50%'}
    RECO = {
        'Normal':  'Routine outpatient follow-up.',
        'Routine': 'Cardiology review within 24 hours.',
        'Urgent':  'Immediate cardiology consultation.',
    }

    def compute(self, d: dict) -> dict:
        h = self._h(d.get('history_suspicion','moderately'))
        e = self._e(d.get('ecg_result','nonspecific_repol'))
        a = self._a(int(d.get('age',60)))
        r = self._r(d.get('risk_factors',[]))
        t = self._t(float(d.get('troponin_ratio',1.0)))
        total = h+e+a+r+t
        tier  = 'Normal' if total<=3 else 'Routine' if total<=6 else 'Urgent'
        return {'heart_score':total,'component_scores':{'H':h,'E':e,'A':a,'R':r,'T':t},
                'triage_tier':tier,'mace_10day_probability':self.MACE[tier],
                'recommended_action':self.RECO[tier]}

    def _h(self,s): return {'slightly_nonspecific':0,'moderately':1,'highly_suspicious':2}.get(s,1)
    def _e(self,e): return {'normal':0,'nonspecific_repol':1,'significant_deviation':2}.get(e,1)
    def _a(self,a): return 0 if a<45 else 1 if a<65 else 2
    def _t(self,t): return 0 if t<=1 else 1 if t<=3 else 2
    def _r(self,f):
        known={'diabetes','hypertension','hypercholesterolemia','obesity','smoking','family_history','atherosclerosis'}
        n=len(set(x.lower() for x in f)&known)
        return 0 if n==0 else 1 if n<=2 else 2

if __name__=='__main__':
    s=HEARTScorer()
    # Known high-risk case: should score 10
    r=s.compute({'history_suspicion':'highly_suspicious',
                 'ecg_result':'significant_deviation','age':70,
                 'risk_factors':['diabetes','hypertension','smoking'],
                 'troponin_ratio':4.0})
    print('Score:', r['heart_score'], '— Expected: 10')
    assert r['heart_score']==10, 'HEART score formula is wrong!'
    print('heart_score.py OK')

