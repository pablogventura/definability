#!/usr/bin/env python
# -*- coding: utf8 -*-


class EFGame(object):
    def __init__(self, a, b, strategy):
        self.a = a
        self.b = b
        self.strategy = strategy
        
    def run_round(self, spoiler_moves):
        result = dict()
        
        for (model_s,item_s) in spoiler_moves:
            modeld,itemd = self.strategy(self.a,self.b,5,result,(model_s,item_s))

            if model_s == self.a:
                result[item_s] = itemd
            elif model_s == self.b:
                result[itemd] = item_s
        
        return result


def strategy(a,b,n,history, move_s):
    model_s,item_s=move_s
    if model_s == a:
        model_d = b
        if item_s in history.keys():
            return model_d, history[item_s]
        else:
            # hay que elegir en b
            return model_d, list(set(model_d.universe) - set(history.values()))[0]
    elif model_s == b:
        model_d = a
        historyinv = {v:k for k,v in history.items()}
        if item_s in historyinv.keys():
            return model_d, historyinv[item_s]
        else:
            # hay que elegir en a
            return model_d, list(set(model_d.universe) - set(historyinv.values()))[0]
    else:
        assert False
