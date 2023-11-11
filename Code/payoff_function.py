class PayoffFunctions:
    def payoff_original(Spath, initial=3487.05, V=1743.525, parti=1.5, denom=1000):
        m = len(Spath)
        Smin = min(Spath)
        if Smin > V:
            payoff = max(denom, denom*(1+parti*(Spath[m-1]/initial-1)))
        else:
            payoff = denom*(Spath[m-1]/initial)
        return payoff
    
    def payoff_no_barrier(ST, initial=3487.05, parti=1.5, denom=1000):
        if ST >= initial:
            payoff = denom*(1+parti*(ST/initial-1))
        else:
            payoff = denom*(ST/initial)
        return payoff