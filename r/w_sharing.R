require(ggplot2)
library(sqldf)
source("sigh_methods.R")

files = c("/Users/jg1g12/Downloads/1_women_sharing_mw.db", "/Users/jg1g12/Downloads/2_women_sharing_mw.db", "/Users/jg1g12/Downloads/3_women_sharing_mw.db", "/Users/jg1g12/Downloads/4_women_sharing_mw.db", "/Users/jg1g12/Downloads/5_women_sharing_mw.db", "/Users/jg1g12/Downloads/6_women_sharing_mw.db", "/Users/jg1g12/Downloads/7_women_sharing_mw.db", "/Users/jg1g12/Downloads/8_women_sharing_mw.db", "/Users/jg1g12/Downloads/9_women_sharing_mw.db", "/Users/jg1g12/Downloads/10_women_sharing_mw.db")
#files = c("/Users/jg1g12/Downloads/5_women_sharing_mw.db", "/Users/jg1g12/Downloads/2_women_sharing_mw.db")
for(x in files) {
    df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where appointment=999", dbname=sprintf(x, 1))
    params <- sqldf("select decision_rule_signaller, women_0, decision_rule_responder, game, women_share_prob, signaller_share_weight, mw_1, mw_2, hash from parameters", dbname=x)
    print(sprintf("Loaded 1 %s", x))
    df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
    for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
        d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
        dir = "../figures"
            if(d$women_0 > 0.8) {
                dir = sprintf("%s/alspac", dir)
            }
        sig = as.character(d$decision_rule_signaller)[1]
        res = as.character(d$decision_rule_responder)[1]
        game = as.character(d$game)[1]
        d <- aggregate(d, by=list(d$women_share_prob, d$signaller_share_weight), FUN=mean)
        d$decision_rule_signaller = sig
        d$decision_rule_responder = res
        d$game = game

        c <- ggplot(d, aes(x=women_share_prob, y=signaller_share_weight))
        png(sprintf("%s/women_sharing_right_calls_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
        print(c + geom_tile(aes(fill=all_right_calls_upto, width=0.1, height=0.1)))
        dev.off()

        png(sprintf("%s/women_sharing_false_positives_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
        print(c + geom_tile(aes(fill=false_positives)))
        dev.off()

        png(sprintf("%s/women_sharing_false_negatives_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
        print(c + geom_tile(aes(fill=false_negatives_upto)))
        dev.off()

        png(sprintf("%s/women_sharing_type_2_misses_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
        print(c + geom_tile(aes(fill=type_2_misses)))
        dev.off()

        png(sprintf("%s/women_sharing_payoffs_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
        print(c + geom_tile(aes(fill=accrued_payoffs)))
        dev.off()
        rm(d)
    }
    print("Made figures.")
    rm(df)
}

files = c("/Users/jg1g12/Downloads/1_women_sharing_women.db", "/Users/jg1g12/Downloads/2_women_sharing_women.db", "/Users/jg1g12/Downloads/3_women_sharing_women.db", "/Users/jg1g12/Downloads/4_women_sharing_women.db", "/Users/jg1g12/Downloads/5_women_sharing_women.db", "/Users/jg1g12/Downloads/6_women_sharing_women.db", "/Users/jg1g12/Downloads/7_women_sharing_women.db", "/Users/jg1g12/Downloads/8_women_sharing_women.db", "/Users/jg1g12/Downloads/9_women_sharing_women.db", "/Users/jg1g12/Downloads/10_women_sharing_women.db")

for(x in files) {
    df <- load(x)
    ##df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
    #df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
    print("Merged.")
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)
            dir = "../figures"
            if(d$women_0 > 0.8) {
                dir = sprintf("%s/alspac", dir)
            }

            for(j in 0:2) {
                png(sprintf("%s/women_sharing_num_rounds_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = num_rounds_type(d, j, "women_share_prob", "signaller_share_weight")
                print(c)
                dev.off()
                png(sprintf("%s/women_sharing_payoffs_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "women_share_prob", "signaller_share_weight")
                print(c)
                dev.off()
                for(k in 0:2) {
                    png(sprintf("%s/women_sharing_signal_%d_%s_%s_type_%d_women.png", dir, k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j, k, "women_share_prob", "signaller_share_weight")
                    print(c)
                    dev.off()
                }
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}