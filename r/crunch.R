args <- commandArgs(trailingOnly = TRUE)

source_dir = args[1]
output_dir = args[2]
start = as.integer(args[3])
end = as.integer(args[4])
lib_loc = args[5]
if(is.na(lib_loc)) {
	lib_loc = NULL
}

library(proto, lib.loc=lib_loc)
library(gsubfn, lib.loc=lib_loc)
library(chron, lib.loc=lib_loc)
library(RSQLite.extfuns, lib.loc=lib_loc)
library(sqldf, lib.loc=lib_loc)
library(ggplot2, lib.loc=lib_loc)
source("sigh_methods.R")

ignore <- function() {
    for(j in 0:2) {
                png(sprintf("%s/mw_sharing_num_rounds_%s_%s_type_%d_women_round_%d.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j, appn))
                c = num_rounds_type(d, j, "mw_share_prob", "responder_share_weight")
                print(c)
                dev.off()
                #png(sprintf("%s/mw_sharing_payoffs_%s_%s_type_%d_women_round_%d.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j, appn))
                #c = payoffs_type(d, j, "mw_share_prob", "responder_share_weight")
                #print(c)
                #dev.off()
                for(k in 0:2) {
                    png(sprintf("%s/mw_sharing_signal_%d_%s_%s_type_%d_women_round_%d.png", dir, k, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], j, appn))
                    c = signals_type(d, j, k, "mw_share_prob", "responder_share_weight")
                    print(c)
                    dev.off()
                }
            }
}

#files = c("%s/1_mw_sharing_mw.db", "%s/2_mw_sharing_mw.db", "%s/3_mw_sharing_mw.db", "%s/4_mw_sharing_mw.db", "%s/5_mw_sharing_mw.db", "%s/6_mw_sharing_mw.db", "%s/7_mw_sharing_mw.db", "%s/8_mw_sharing_mw.db", "%s/9_mw_sharing_mw.db", "%s/10_mw_sharing_mw.db")
files = c("%s/sharing_mw.db", "%s/prospect_mw.db", "%s/payoff_mw.db", "%s/lexic_mw.db", "%s/payoff_prospect_mw.db")
#files = c("%s/prospect_mw.db", "%s/payoff_mw.db", "%s/lexic_mw.db")#, "%s/payoff_prospect_mw.db")
for(x in files) {
	x <- sprintf(x, source_dir)
	for(appn in start:end) {
	df <- load(x, appn)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		dir = output_dir
			if(d$women_0 > 0.8) {
				dir = sprintf("%s/alspac", dir)
			}
		sig = as.character(d$decision_rule_signaller)[1]
		res = as.character(d$decision_rule_responder)[1]
		game = as.character(d$game)[1]
		d <- aggregate(d, by=list(d$mw_share_prob, d$responder_share_weight), FUN=mean)
		d$decision_rule_signaller = sig
		d$decision_rule_responder = res
		d$game = game

		c <- ggplot(d, aes(x=mw_share_prob, y=responder_share_weight, z=all_right_calls_upto, fill=all_right_calls_upto))
		png(sprintf("%s/mw_sharing_right_calls_%s_%s_%s_%d.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1], appn))
		print(c + geom_tile())
		dev.off()


		png(sprintf("%s/mw_sharing_false_negatives_%s_%s_%s_%d.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1], appn))
		c <- ggplot(d, aes(x=mw_share_prob, y=responder_share_weight, z=false_negatives_upto, fill=false_negatives_upto))
		print(c + geom_tile())# + scale_fill_gradient(limits = c(0, 1.0)))
		dev.off()

		png(sprintf("%s/mw_sharing_false_positives_%s_%s_%s_%d.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1], appn))
		c <- ggplot(d, aes(x=mw_share_prob, y=responder_share_weight, z=false_positives_upto, fill=false_positives_upto))
		print(c + geom_tile())
		dev.off()

		#png(sprintf("%s/mw_sharing_payoffs_%s_%s_%s_%d.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1], appn))
		#c <- ggplot(d, aes(x=mw_share_prob, y=responder_share_weight, z=accrued_payoffs))
		#print(c + geom_tile())
		#dev.off()
		rm(d)
	}
}
	print("Made figures.")
	rm(df)
}

#files = c("%s/1_mw_sharing_women.db", "%s/2_mw_sharing_women.db", "%s/3_mw_sharing_women.db", "%s/4_mw_sharing_women.db", "%s/5_mw_sharing_women.db", "%s/6_mw_sharing_women.db", "%s/7_mw_sharing_women.db", "%s/8_mw_sharing_women.db", "%s/9_mw_sharing_women.db", "%s/10_mw_sharing_women.db")
#files = c("%s/5_mw_sharing_women.db", "%s/2_mw_sharing_women.db")
files = c("%s/sharing_w.db", "%s/prospect_w.db", "%s/payoff_w.db", "%s/lexic_w.db", "%s/payoff_prospect_w.db")
#files = c("%s/prospect_w.db", "%s/payoff_w.db", "%s/lexic_w.db")#, "%s/payoff_prospect_w.db")
for(x in files) {
	x <- sprintf(x, source_dir)
	for(appn in start:end) {
    df <- load(x)
    ##df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
    #df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
    print("Merged.")
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)
            dir = output_dir
            if(d$women_0 > 0.8) {
                dir = sprintf("%s/alspac", dir)
            }
            png(sprintf("%s/mw_sharing_num_rounds_%s_%s_round_%d.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], appn))
                c = rounds_diff(d, "mw_share_prob", "responder_share_weight")
                print(c)
                dev.off()

            rm(d)
    }
    print("Made figures.")
    rm(df)
}
}

#files = c("%s/1_women_sharing_mw.db", "%s/2_women_sharing_mw.db", "%s/3_women_sharing_mw.db", "%s/4_women_sharing_mw.db", "%s/5_women_sharing_mw.db", "%s/6_women_sharing_mw.db", "%s/7_women_sharing_mw.db", "%s/8_women_sharing_mw.db", "%s/9_women_sharing_mw.db", "%s/10_women_sharing_mw.db")
files = c("%s/w_payoff_mw.db", "%s/w_lexic_mw.db")
#files = c("%s/w_sharing_mw.db", "%s/w_prospect_mw.db", "%s/w_payoff_mw.db", "%s/w_lexic_mw.db", "%s/w_payoff_prospect_mw.db")
for(x in files) {
	x <- sprintf(x, source_dir)
	for(appn in start:end) {
    df <- load(x)
    for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
        d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
        dir = output_dir
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

        png(sprintf("%s/women_sharing_right_calls_%s_%s_%s_round_%d.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1], appn))
        c <- ggplot(d, aes(x=women_share_prob, y=signaller_share_weight, z=all_right_calls_upto, fill=all_right_calls_upto))
        print(c + geom_tile())
        dev.off()

        png(sprintf("%s/women_sharing_false_positives_%s_%s_%s_round_%d.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1], appn))
        c <- ggplot(d, aes(x=women_share_prob, y=signaller_share_weight, z=false_positives_upto, fill=false_positives_upto))
        print(c + geom_tile())
        dev.off()

        png(sprintf("%s/women_sharing_false_negatives_%s_%s_%s_round_%d.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1], appn))
        c <- ggplot(d, aes(x=women_share_prob, y=signaller_share_weight, z=false_negatives_upto, fill=false_negatives_upto))
        print(c + geom_tile())
        dev.off()

        #png(sprintf("%s/women_sharing_payoffs_%s_%s_%s_round_%d.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1], appn))
        #c <- ggplot(d, aes(x=women_share_prob, y=signaller_share_weight, z=accrued_payoffs))
        #print(c + geom_tile())
        #dev.off()
        rm(d)
    }
    print("Made figures.")
    rm(df)
}
}

#files = c("%s/w_sharing_w.db", "%s/w_prospect_w.db", "%s/w_payoff_w.db", "%s/w_lexic_w.db", "%s/w_payoff_prospect_w.db")
files = c("%s/w_payoff_w.db", "%s/w_lexic_w.db")
for(x in files) {
	x <- sprintf(x, source_dir)
	for(appn in start:end) {
    df <- load(x)
    ##df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
    #df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
    print("Merged.")
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)
            dir = output_dir
            if(d$women_0 > 0.8) {
                dir = sprintf("%s/alspac", dir)
            }
            png(sprintf("%s/women_sharing_num_rounds_%s_%s_round_%d.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1], appn))
            c = rounds_diff(df, "women_share_prob", "signaller_share_weight")
            print(c)
            dev.off()
            rm(d)
    }
    print("Made figures.")
    rm(df)
}
}