require(ggplot2)
library(sqldf)
files = c("/Users/jg1g12/Downloads/6_women_proportions__mw_%s.db", "/Users/jg1g12/Downloads/8_women_proportions__mw_%s.db", "/Users/jg1g12/Downloads/9_women_proportions__mw_%s.db", "/Users/jg1g12/Downloads/12_women_proportions__mw_%s.db", "/Users/jg1g12/Downloads/13_women_proportions__mw_%s.db", "/Users/jg1g12/Downloads/14_women_proportions__mw_%s.db")
for(x in files) {
	df <- sqldf("select decision_rule_signaller, decision_rule_responder, game, all_right_calls_upto, false_positives, false_negatives_upto, women_1, women_2 from results join parameters where num_rounds=999 AND game='carrying_referral'", dbname=sprintf(x, 1))
	print("Loaded 1..")
	for(i in 2:16) {
		df = rbind(df, sqldf("select decision_rule_signaller, decision_rule_responder, game, all_right_calls_upto, false_positives, false_negatives_upto, women_1, women_2 from results join parameters where num_rounds=999 AND game='carrying_referral'", dbname=sprintf(x, i)))
		print(sprintf("Loaded %d - %s.", i, x))
	}
	for(i in unique(interaction(df$decision_rule_signaller, df$decision_rule_responder, df$game))) {
		d <- subset(df, interaction(df$decision_rule_signaller, df$decision_rule_responder, df$game) == i)
		c <- ggplot(d, aes(x=women_1, y=women_2))
		png(sprintf("../figures/right_calls_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
		dev.off()

		png(sprintf("../figures/false_positives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_positives)))
		dev.off()

		png(sprintf("../figures/false_negatives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_negatives_upto)))
		dev.off()
		rm(d)
	}
	print("Made figures.")
	rm(df)
}