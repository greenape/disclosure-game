require(ggplot2)
library(sqldf)

files = c("/Users/jg1g12/Downloads/1_women_proportions_mw.db", "/Users/jg1g12/Downloads/2_women_proportions_mw.db", "/Users/jg1g12/Downloads/3_women_proportions_mw.db")
for(x in files) {
	df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where appointment=999", dbname=x)
	params <- sqldf("select decision_rule_signaller, women_0, decision_rule_responder, game, mw_share_width, mw_share_bias, women_1, women_2, hash from parameters", dbname=x)
	print(sprintf("Loaded %s", x))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		dir = "../figures"
		
		c <- ggplot(d, aes(x=women_1, y=women_2))
		png(sprintf("%s/women_proportions_right_calls_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
		dev.off()

		png(sprintf("%s/women_proportions_false_positives_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_positives)))
		dev.off()

		png(sprintf("%s/women_proportions_false_negatives_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_negatives_upto)))
		dev.off()

		png(sprintf("%s/women_proportions_type_2_misses_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=type_2_misses)))
		dev.off()

		png(sprintf("%s/women_proportions_payoffs_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=accrued_payoffs)))
		dev.off()
		rm(d)
	}
	print("Made figures.")
	rm(df)
}

files = c("/Users/jg1g12/Downloads/1_mw_proportions_mw.db", "/Users/jg1g12/Downloads/2_mw_proportions_mw.db", "/Users/jg1g12/Downloads/3_mw_proportions_mw.db", "/Users/jg1g12/Downloads/4_mw_proportions_mw.db", "/Users/jg1g12/Downloads/5_mw_proportions_mw.db", "/Users/jg1g12/Downloads/6_mw_proportions_mw.db")
for(x in files) {
	df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where appointment=999", dbname=x)
	params <- sqldf("select decision_rule_signaller, women_0, decision_rule_responder, game, mw_share_width, mw_share_bias, mw_1, mw_2, hash from parameters", dbname=x)
	print(sprintf("Loaded 1 %s", x))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {

		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		dir = "../figures"
			if(d$women_0 > 0.8) {
				dir = sprintf("%s/alspac", dir)
			}
		c <- ggplot(d, aes(x=mw_1, y=mw_2))
		png(sprintf("%s/mw_proportions_right_calls_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
		dev.off()

		png(sprintf("%s/mw_proportions_false_positives_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_positives)))
		dev.off()

		png(sprintf("%s/mw_proportions_false_negatives_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_negatives_upto)))
		dev.off()

		png(sprintf("%s/mw_proportions_type_2_misses_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=type_2_misses)))
		dev.off()

		png(sprintf("%s/mw_proportions_payoffs_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=accrued_payoffs)))
		dev.off()
		rm(d)
	}
	print("Made figures.")
	rm(df)
}

files = c("/Users/jg1g12/Downloads/1_mw_sharing_mw.db", "/Users/jg1g12/Downloads/2_mw_sharing_mw.db", "/Users/jg1g12/Downloads/3_mw_sharing_mw.db", "/Users/jg1g12/Downloads/4_mw_sharing_mw.db", "/Users/jg1g12/Downloads/5_mw_sharing_mw.db", "/Users/jg1g12/Downloads/6_mw_sharing_mw.db")
for(x in files) {
	df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where appointment=999", dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, women_0, decision_rule_responder, game, mw_share_width, mw_share_bias, mw_1, mw_2, hash from parameters", dbname=x)
	print(sprintf("Loaded 1 %s", x))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		dir = "../figures"
			if(d$women_0 > 0.8) {
				dir = sprintf("%s/alspac", dir)
			}
		c <- ggplot(d, aes(x=mw_share_width, y=mw_share_bias))
		png(sprintf("%s/mw_sharing_right_calls_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
		dev.off()

		png(sprintf("%s/mw_sharing_false_positives_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_positives)))
		dev.off()

		png(sprintf("%s/mw_sharing_false_negatives_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_negatives_upto)))
		dev.off()

		png(sprintf("%s/mw_sharing_type_2_misses_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=type_2_misses)))
		dev.off()

		png(sprintf("%s/mw_sharing_payoffs_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=accrued_payoffs)))
		dev.off()
		rm(d)
	}
	print("Made figures.")
	rm(df)
}

files = c("/Users/jg1g12/Downloads/1_women_sharing_mw.db", "/Users/jg1g12/Downloads/2_women_sharing_mw.db", "/Users/jg1g12/Downloads/3_women_sharing_mw.db", "/Users/jg1g12/Downloads/4_women_sharing_mw.db", "/Users/jg1g12/Downloads/5_women_sharing_mw.db", "/Users/jg1g12/Downloads/6_women_sharing_mw.db")
for(x in files) {
	df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where appointment=999", dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, women_0, decision_rule_responder, game, women_share_width, women_share_bias, hash from parameters", dbname=sprintf(x, 1))
	print(sprintf("Loaded 1 %s", x))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		dir = "../figures"
			if(d$women_0 > 0.8) {
				dir = sprintf("%s/alspac", dir)
			}
		c <- ggplot(d, aes(x=women_share_width, y=women_share_bias))
		png(sprintf("%s/women_sharing_right_calls_%s_%s_%s.png", dir, as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
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