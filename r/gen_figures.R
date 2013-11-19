source("figures.R")

figures("lexicographic", "lexicographic", "heuristic", "heuristic", "results/alspac", "alspac")
figures("lexicographic", "lexicographic", "heuristic_ref", "heuristic_ref", "results/alspac", "alspac")
figures("bayes_payoff", "bayes_payoff", "payoff", "payoff", "results/alspac", "alspac")
figures("bayes_payoff", "bayes_payoff", "payoff_ref", "payoff_ref", "results/alspac", "alspac")

figures("bayes", "recognition", "standard", "standard_bayes_recog", "results/alspac", "alspac")
figures("recognition", "bayes", "standard", "standard_recog_bayes", "results/alspac", "alspac")
figures("bayes", "bayes", "standard", "standard_bayes", "results/alspac", "alspac")
figures("recognition", "recognition", "standard", "standard_recog", "results/alspac", "alspac")

figures("bayes", "recognition", "referral", "ref_bayes_recog", "results/alspac", "alspac")
figures("recognition", "bayes", "referral", "ref_recog_bayes", "results/alspac", "alspac")
figures("bayes", "bayes", "referral", "ref_bayes", "results/alspac", "alspac")
figures("recognition", "recognition", "referral", "ref_recog", "results/alspac", "alspac")

figures("bayes", "recognition", "recognition", "recog_bayes_recog", "results/alspac", "alspac")
figures("recognition", "bayes", "recognition", "recog_recog_bayes", "results/alspac", "alspac")
figures("bayes", "bayes", "recognition", "recog_bayes", "results/alspac", "alspac")
figures("recognition", "recognition", "recognition", "recog_recog", "results/alspac", "alspac")