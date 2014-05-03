require(ggplot2)
require(sqldf)
source("sigh_methods.R")

#files = c("/Users/jg1g12/Download_sqlites/1_women_proportions_women.db", "/Users/jg1g12/Download_sqlites/2_women_proportions_women.db", "/Users/jg1g12/Download_sqlites/3_women_proportions_women.db")
files = c("/Users/jg1g12/Download_sqlites/4_women_proportions_women.db")
for(x in files) {
    df <- load_sqlite(x)
    ##df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
    #df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
    print("Merged.")
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)

            for(j in 0:2) {
                png(sprintf("../figures/women_proportions_num_rounds_%s_%s_type_%d_women.png", as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = num_rounds_type(d, j, "women_1", "women_2")
                print(c)
                dev.off()
                print("Num rounds.")
                png(sprintf("../figures/women_proportions_payoffs_%s_%s_type_%d_women.png", as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "women_1", "women_2")
                print(c)
                dev.off()
                print("Payoffs")
                for(k in 0:2) {
                    png(sprintf("../figures/women_proportions_signal_%d_%s_%s_type_%d_women.png", k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j, k, "women_1", "women_2")
                    print(c)
                    dev.off()

                }
                print("Signals.")
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}

#files = c("/Users/jg1g12/Download_sqlites/1_mw_proportions_women.db", "/Users/jg1g12/Download_sqlites/2_mw_proportions_women.db", "/Users/jg1g12/Download_sqlites/3_mw_proportions_women.db", "/Users/jg1g12/Download_sqlites/4_mw_proportions_women.db", "/Users/jg1g12/Download_sqlites/5_mw_proportions_women.db", "/Users/jg1g12/Download_sqlites/6_mw_proportions_women.db")
files = c("/Users/jg1g12/Download_sqlites/7_mw_proportions_women.db", "/Users/jg1g12/Download_sqlites/8_mw_proportions_women.db")
for(x in files) {
    df <- load_sqlite(x)
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
                file = sprintf("%s/mw_proportions_num_rounds_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j)
                png()
                c = num_rounds_type(d, j, "mw_1", "mw_2")
                print(c)
                dev.off()
                png(sprintf("%s/mw_proportions_payoffs_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "mw_1", "mw_2")
                print(c)
                dev.off()
                for(k in 0:2) {
                    png(sprintf("%s/mw_proportions_signal_%d_%s_%s_type_%d_women.png", dir, k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j,k,  "mw_1", "mw_2")
                    print(c)
                    dev.off()
                }
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}

files = c("/Users/jg1g12/Download_sqlites/1_mw_sharing_women.db", "/Users/jg1g12/Download_sqlites/2_mw_sharing_women.db", "/Users/jg1g12/Download_sqlites/3_mw_sharing_women.db", "/Users/jg1g12/Download_sqlites/4_mw_sharing_women.db", "/Users/jg1g12/Download_sqlites/5_mw_sharing_women.db", "/Users/jg1g12/Download_sqlites/6_mw_sharing_women.db")
for(x in files) {
    df <- load_sqlite(x)
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
                png(sprintf("%s/mw_sharing_num_rounds_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = num_rounds_type(d, j, "mw_share_width", "mw_share_bias")
                print(c)
                dev.off()
                png(sprintf("%s/mw_sharing_payoffs_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "mw_share_width", "mw_share_bias")
                print(c)
                dev.off()
                for(k in 0:2) {
                    png(sprintf("%s/mw_sharing_signal_%d_%s_%s_type_%d_women.png", dir, k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j, k, "mw_share_width", "mw_share_bias")
                    print(c)
                    dev.off()
                }
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}

files = c("/Users/jg1g12/Download_sqlites/1_women_sharing_women.db", "/Users/jg1g12/Download_sqlites/2_women_sharing_women.db", "/Users/jg1g12/Download_sqlites/3_women_sharing_women.db", "/Users/jg1g12/Download_sqlites/4_women_sharing_women.db", "/Users/jg1g12/Download_sqlites/5_women_sharing_women.db", "/Users/jg1g12/Download_sqlites/6_women_sharing_women.db")
for(x in files) {
    df <- load_sqlite(x)
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
                c = num_rounds_type(d, j, "women_share_width", "women_share_bias")
                print(c)
                dev.off()
                png(sprintf("%s/women_sharing_payoffs_%s_%s_type_%d_women.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                c = payoffs_type(d, j, "women_share_width", "women_share_bias")
                print(c)
                dev.off()
                for(k in 0:2) {
                    png(sprintf("%s/women_sharing_signal_%d_%s_%s_type_%d_women.png", dir, k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j))
                    c = signals_type(d, j, k, "women_share_width", "women_share_bias")
                    print(c)
                    dev.off()
                }
            }
            rm(d)
    }
    print("Made figures.")
    rm(df)
}