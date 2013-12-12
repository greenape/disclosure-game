require(ggplot2)
library(sqldf)

files = c("/Users/jg1g12/Downloads/1_women_proportions_mw_%s.db", "/Users/jg1g12/Downloads/2_women_proportions_mw_%s.db", "/Users/jg1g12/Downloads/3_women_proportions_mw_%s.db")
for(x in files) {
	df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where num_rounds=1000", dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, decision_rule_responder, game, mw_share_width, mw_share_bias, hash from parameters", dbname=sprintf(x, 1))
	print("Loaded 1..")
	for(i in 2:16) {
		df = rbind(df, sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where num_rounds=1000", dbname=sprintf(x, i)))
		params = rbind(params, sqldf("select decision_rule_signaller, decision_rule_responder, game, mw_share_width, mw_share_bias, hash from parameters", dbname=sprintf(x, i)))
		print(sprintf("Loaded %d - %s.", i, sprintf(x, i)))
	}
	df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		c <- ggplot(d, aes(x=mw_share_width, y=mw_share_bias))
		png(sprintf("../figures/women_proportions_right_calls_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
		dev.off()

		png(sprintf("../figures/women_proportions_false_positives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_positives)))
		dev.off()

		png(sprintf("../figures/women_proportions_false_negatives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_negatives_upto)))
		dev.off()

		png(sprintf("../figures/women_proportions_type_2_misses_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=type_2_misses)))
		dev.off()

		png(sprintf("../figures/women_proportions_payoffs_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=accrued_payoffs)))
		dev.off()
		rm(d)
	}
	print("Made figures.")
	rm(df)
}

files = c("/Users/jg1g12/Downloads/1_mw_proportions_mw_%s.db", "/Users/jg1g12/Downloads/2_mw_proportions_mw_%s.db", "/Users/jg1g12/Downloads/3_mw_proportions_mw_%s.db")
for(x in files) {
	df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where num_rounds=1000", dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, decision_rule_responder, game, mw_share_width, mw_share_bias, hash from parameters", dbname=sprintf(x, 1))
	print("Loaded 1..")
	for(i in 2:16) {
		df = rbind(df, sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where num_rounds=1000", dbname=sprintf(x, i)))
		params = rbind(params, sqldf("select decision_rule_signaller, decision_rule_responder, game, mw_share_width, mw_share_bias, hash from parameters", dbname=sprintf(x, i)))
		print(sprintf("Loaded %d - %s.", i, sprintf(x, i)))
	}
	df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		c <- ggplot(d, aes(x=mw_share_width, y=mw_share_bias))
		png(sprintf("../figures/mw_proportions_right_calls_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
		dev.off()

		png(sprintf("../figures/mw_proportions_false_positives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_positives)))
		dev.off()

		png(sprintf("../figures/mw_proportions_false_negatives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_negatives_upto)))
		dev.off()

		png(sprintf("../figures/mw_proportions_type_2_misses_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=type_2_misses)))
		dev.off()

		png(sprintf("../figures/mw_proportions_payoffs_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=accrued_payoffs)))
		dev.off()
		rm(d)
	}
	print("Made figures.")
	rm(df)
}

files = c("/Users/jg1g12/Downloads/1_mw_sharing_mw_%s.db", "/Users/jg1g12/Downloads/2_mw_sharing_mw_%s.db", "/Users/jg1g12/Downloads/3_mw_sharing_mw_%s.db")
for(x in files) {
	df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where num_rounds=1000", dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, decision_rule_responder, game, mw_share_width, mw_share_bias, hash from parameters", dbname=sprintf(x, 1))
	print("Loaded 1..")
	for(i in 2:16) {
		df = rbind(df, sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where num_rounds=1000", dbname=sprintf(x, i)))
		params = rbind(params, sqldf("select decision_rule_signaller, decision_rule_responder, game, mw_share_width, mw_share_bias, hash from parameters", dbname=sprintf(x, i)))
		print(sprintf("Loaded %d - %s.", i, sprintf(x, i)))
	}
	df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		c <- ggplot(d, aes(x=mw_share_width, y=mw_share_bias))
		png(sprintf("../figures/mw_sharing_right_calls_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
		dev.off()

		png(sprintf("../figures/mw_sharing_false_positives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_positives)))
		dev.off()

		png(sprintf("../figures/mw_sharing_false_negatives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_negatives_upto)))
		dev.off()

		png(sprintf("../figures/mw_sharing_type_2_misses_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=type_2_misses)))
		dev.off()

		png(sprintf("../figures/mw_sharing_payoffs_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=accrued_payoffs)))
		dev.off()
		rm(d)
	}
	print("Made figures.")
	rm(df)
}

files = c("/Users/jg1g12/Downloads/1_women_sharing_mw_%s.db", "/Users/jg1g12/Downloads/2_women_sharing_mw_%s.db", "/Users/jg1g12/Downloads/3_women_sharing_mw_%s.db")
for(x in files) {
	df <- sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where num_rounds=1000", dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, decision_rule_responder, game, women_share_width, women_share_bias, hash from parameters", dbname=sprintf(x, 1))
	print("Loaded 1..")
	for(i in 2:16) {
		df = rbind(df, sqldf("select type_2_misses, accrued_payoffs, all_right_calls_upto, false_positives, false_negatives_upto, hash from results where num_rounds=1000", dbname=sprintf(x, i)))
		params = rbind(params, sqldf("select decision_rule_signaller, decision_rule_responder, game, women_share_width, women_share_bias, hash from parameters", dbname=sprintf(x, i)))
		print(sprintf("Loaded %d - %s.", i, sprintf(x, i)))
	}
	df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	for(i in unique(interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder))) {
		d <- subset(df, interaction(df$game, df$decision_rule_signaller, df$decision_rule_responder) == i)
		c <- ggplot(d, aes(x=women_share_width, y=women_share_bias))
		png(sprintf("../figures/women_sharing_right_calls_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=all_right_calls_upto)))
		dev.off()

		png(sprintf("../figures/women_sharing_false_positives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_positives)))
		dev.off()

		png(sprintf("../figures/women_sharing_false_negatives_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=false_negatives_upto)))
		dev.off()

		png(sprintf("../figures/women_sharing_type_2_misses_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=type_2_misses)))
		dev.off()

		png(sprintf("../figures/women_sharing_payoffs_%s_%s_%s.png", as.character(d$decision_rule_signaller)[1], as.character(d$decision_rule_responder)[1], as.character(d$game)[1]))
		print(c + geom_tile(aes(fill=accrued_payoffs)))
		dev.off()
		rm(d)
	}
	print("Made figures.")
	rm(df)
}