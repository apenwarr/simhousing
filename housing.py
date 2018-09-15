#!/usr/bin/python -u
import csv
import math
import random

# minimum initial selling price by construction company
PRICE_FLOOR = 10000

# after-tax $/year
INCOME = 100000

# max frac of after-tax income to spend on housing payments
MAX_SPEND = 0.6

# optimal value of a home (with no commute)
MAX_VALUE = INCOME * MAX_SPEND

# decline in value (wasted time due to commute) per unit of distance
DISTANCE_FACTOR = 0.995

# fraction of mortgage principal in payments per year (assumed forever)
MORTGAGE = 0.05

# Annual property tax rate, as fraction of purchase price
# https://www.trulia.com/voices/Rent_vs_Buy/How_do_I_find_out_the_property_tax_rate_in_Cuperti-342422
PROP_TAX = 0.0125


def randpos():
  return random.normalvariate(0, 10)


def randsize():
  return 1 + abs(random.normalvariate(0, 5))


def randgrowth():
  return 1 + abs(random.normalvariate(0, 0.02))


class Home(object):
  _v = 0
  
  def __init__(self):
    Home._v += 1
    self.n = Home._v
    self.x = randpos()
    self.y = randpos()
    self.owner = None
    self.sold_price = PRICE_FLOOR
    self.asking_price = None

  def __repr__(self):
    return 'H%02d' % self.n

  # Put a home on the market for the given asking price
  def enlist(self, asking_price):
    self.asking_price = asking_price
    forsale.add(self)
    if self.owner:
      self.owner.enlisted += 1
      assert self.owner.home == self
      self.owner.home = None  # self.owner is kept until actually sold

  # Actually sell the given home for the given price
  def sell(self, price):
    assert self in forsale
    forsale.remove(self)
    if self.owner:
      assert self.owner.home != self
      self.owner.enlisted -= 1
      self.owner.loan -= price
      if self.owner.loan < 0:
        self.owner.profit += -self.owner.loan
        self.owner.loan = 0
    self.sold_price = price
    self.asking_price = None
    self.owner = None

  # Take ownership of the given home for the given price
  def buy(self, owner, price):
    assert not owner.home
    assert not self.owner         # must already be marked sold
    assert self not in forsale    # must not be on the market
    assert not self.asking_price  # must not be on the market
    owner.loan += price
    owner.home = self
    self.sold_price = price
    self.owner = owner
    sales.append(price)
    recent_sales.append(int(price))


class Person(object):
  _v = 0
  
  def __init__(self, employer):
    Person._v += 1
    self.n = Person._v
    self.home = None
    self.employer = employer
    self.loan = 0
    self.profit = 0
    self.enlisted = 0

  def __repr__(self):
    return 'P%02d' % self.n

  # How much revenue would we derive from living in the given home?
  def _revenue(self, home):
    if not home: return 0
    distance = ((self.employer.x - home.x)**2 +
                (self.employer.y - home.y)**2)**.5
    return MAX_VALUE * (DISTANCE_FACTOR ** distance)

  def cur_revenue(self):
    return self._revenue(self.home)

  def cur_costs(self):
    return (self.loan * MORTGAGE +
            (self.home.sold_price if self.home else 0) * PROP_TAX)

  # Net income derived from buying the given home at the given price.
  def buy_value(self, home, price):
    return self._revenue(home) - price * (MORTGAGE + PROP_TAX)

  # Net income we'd lose by selling the given home at the given price,
  # if we bought it at old_price.
  def sell_value(self, home, price, old_price):
    return self._revenue(home) - price * MORTGAGE - old_price * PROP_TAX

  # calculate the buying price where buy_value == sell_value, assuming
  # we sell our current home (if any) for sell_price.
  def breakeven_bid(self, home, sell_price):
    if self.home:
      sv = self.sell_value(self.home, sell_price, self.home.sold_price)
    else:
      sv = 0
    rev = self._revenue(home)
    # sell_value = buy_value
    # sv = rev - price * (MORTGAGE + PROP_TAX)
    # price * (MORTGAGE + PROP_TAX) = rev - sv
    price = (rev - sv) / (MORTGAGE + PROP_TAX)
    return price
    

class Employer(object):
  def __init__(self):
    self.x = randpos()
    self.y = randpos()
    self.size = randsize()
    self.growth_rate = randgrowth()


homes = None
employers = None
people = None
forsale = set()
sales = []
recent_sales = []


def avg_price():
  s = sales[-10:]
  if not s:
    s = [h.sold_price for h in homes]
  s.sort()
  return s[len(s)/2]


def dump(i):
  tsc = tpr = 0
  for p in sorted(people, key=lambda p: p.n):
    sc = p.cur_revenue() - p.cur_costs()
    tsc += sc
    tpr += p.profit
    if 1: print ('%4r%s %4r %10dp %6dv %6dc %7ds %11d!' %
           (p, '*' if p.enlisted else ' ',
            p.home,
            p.home.sold_price if p.home else 0,
            p.cur_revenue(),
            p.cur_costs(),
            sc,
            p.profit))
  print ('#%d Score: %d  Profit: %d  Forsale: %d  Avg: %d  P/H: %d/%d %d%%'
         % (i, tsc, tpr, 
            sum(1 for h in homes if not h.owner or h.asking_price),
            avg_price(), len(people), len(homes), 100*len(people)/len(homes)))
  print '  Sales: %r' % (recent_sales,)
  recent_sales[:] = []
  print


def main():
  global homes, employers, people, forsale
  random.seed(1)
  employers = [Employer() for _ in xrange(10)]
  people = []
  for e in employers:
    people += [Person(e) for _ in xrange(int(e.size))]
  homes = [Home() for _ in xrange(int(len(people) * 1.5))]
  for h in homes:
    h.enlist(PRICE_FLOOR)

  w = csv.writer(open('results.csv', 'w'))
  w.writerow(['i', 'Home', 'x', 'y', 'Seller', 'Buyer', 'OldPrice', 'Price', 'NumPeople', 'NumHomes', 'NumForSale'])

  for i in range(85):
    if 1:
      if forsale:
        FACTOR=1.05
        bids = dict((h, (None, h.asking_price/FACTOR)) for h in forsale)
        bidders = set(people)
        while bidders:
          for p in list(bidders):
            sell_price = p.home.sold_price if p.home else 0
            best_h = None
            best_val = None
            for h, (winner_p, bid) in bids.iteritems():
              new_bid = bid * FACTOR
              val = p.buy_value(h, new_bid)
              if val > best_val and new_bid < p.breakeven_bid(h, sell_price):
                best_h = h
                best_val = val
            del h
            if best_h:
              winner_p, bid = bids[best_h]
              new_bid = bid * FACTOR
              beven = p.breakeven_bid(best_h,
                                      p.home.sold_price if p.home else 0)
              print '   ** %r bidding %10d for %r (asking %d, even %d, value %d, cost %d)' % (p, new_bid, best_h, best_h.asking_price, beven, p._revenue(best_h), new_bid*(MORTGAGE + PROP_TAX))
              bids[best_h] = (p, new_bid)
              if winner_p: bidders.add(winner_p)
            # if we bid, we don't need to bid again.
            # if we didn't bid, we're out of our league.
            # either way, take us out of the list.
            bidders.remove(p)

        for h, (winner_p, bid) in bids.iteritems():
          if winner_p:
            print '-- sold %4r %4r->%-4r for %7d (asked %d)' % (h, h.owner, winner_p, bid, h.asking_price)
            w.writerow([i, str(h), h.x, h.y, str(h.owner), str(winner_p),
                        h.sold_price, bid, len(people), len(homes), len(forsale)-1])
            if winner_p.home:
              winner_p.home.enlist(winner_p.home.sold_price)
            h.sell(bid)
            h.buy(winner_p, bid)
      dump(i)
    if i < 25 or i > 40:
      for e in employers:
        oldsize = int(e.size)
        e.size *= e.growth_rate
        newsize = int(e.size)
        if newsize > oldsize:
          for _ in xrange(oldsize, newsize):
            people.append(Person(e))
    else:
      for e in employers:
        oldsize = int(e.size)
        e.size /= e.growth_rate ** 2
        if e.size < 1:
          e.size = 1
        newsize = int(e.size)
        if newsize < oldsize:
          sub = [p for p in people if p.employer == e]
          for p in sub[:oldsize-newsize]:
            if p.home:
              p.home.enlist(PRICE_FLOOR)
              people.remove(p)
    random.shuffle(people)
    if 0: # i in (18, 28, 36):
      # layoffs!
      ndel = len(people) / 3
      for p in people[:ndel]:
        # TODO(apenwarr): not sure what asking price we should use here.
        if p.home:
          p.home.enlist(PRICE_FLOOR)
      people[:ndel] = []
    else:
      for i in xrange(0, len(people)/20, 2):
        # some people switch employers and thus want to change houses.
        # This adds some liquidity to the housing market.
        a, b = people[i], people[i+1]
        a.employer, b.employer = b.employer, a.employer
        if a.home: a.home.enlist(a.home.sold_price * 1.2)
        if b.home: b.home.enlist(b.home.sold_price * 1.2)
    for h in forsale:
      # houses sitting on the market for a while drop their prices
      h.asking_price = max(PRICE_FLOOR, h.asking_price * 0.8)
  print 'Steps: %d' % i


if __name__ == '__main__':
  main()
