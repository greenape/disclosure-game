require(ggplot2)
library(sqldf)
files = c("/Users/jg1g12/Downloads/1_women_proportions_women_%s.db", "/Users/jg1g12/Downloads/2_women_proportions_women_%s.db", "/Users/jg1g12/Downloads/3_women_proportions_women_%s.db")
cols = "player_type, accrued_payoffs, referred, hash"
for(x in files) {
	df <- sqldf(sprintf("select %s from results where num_rounds>0 OR referred=1", cols), dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, decision_rule_responder, game, women_1, women_2, hash from parameters", dbname=sprintf(x, 1))
	print("Loaded 1..")
	for(i in 2:16) {
		df = rbind(df, sqldf(sprintf("select %s from results where num_rounds>0 OR referred=1", cols), dbname=sprintf(x, i)))
		params = rbind(params, sqldf("select decision_rule_signaller, decision_rule_responder, game, women_1, women_2, hash from parameters", dbname=sprintf(x, i)))
		print(sprintf("Loaded %d - %s.", i, sprintf(x, i)))
	}
	#df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	df <- aggregate(df, by=list(Group.women_1=df$women_1, Group.women_2=df$women_2, Group.game=df$game, Group.decision_rule_signaller=df$decision_rule_signaller, Group.decision_rule_responder=df$decision_rule_responder, Group.player_type=df$player_type), FUN=mean)
	for(i in unique(interaction(df$Group.game, df$Group.decision_rule_signaller, df$Group.decision_rule_responder))) {
		d <- subset(df, interaction(df$Group.game, df$Group.decision_rule_signaller, df$Group.decision_rule_responder) == i)
		c <- ggplot(d, aes(x=women_1, y=women_2))
				png(sprintf("../figures/payoffs_%s_%s_%s_women.png", as.character(d$Group.decision_rule_signaller)[1], as.character(d$Group.decision_rule_responder)[1], as.character(d$Group.game)[1], i))
				print(c + geom_tile(aes(fill=accrued_payoffs)))
				dev.off()
		for(k in 0:2) {
					png(sprintf("../figures/honest_signals_%s_%s_%s_type_%d_women.png", as.character(d$Group.decision_rule_signaller)[1], as.character(d$Group.decision_rule_responder)[1], as.character(d$Group.game)[1], j))
					signal = eval(parse(text=sprintf("d$signal_%d_frequency", j)))
					print(c + geom_tile(aes(fill=signal)))
					dev.off()
				}
		for(j in 0:2) {
			typed = subset(d, d$Group.player_type == j)
			if(nrow(typed) > 0) {
				c <- ggplot(typed, aes(x=women_1, y=women_2))
				png(sprintf("../figures/payoffs_%s_%s_%s_type_%d.png", as.character(d$Group.decision_rule_signaller)[1], as.character(d$Group.decision_rule_responder)[1], as.character(d$Group.game)[1], j))
				print(c + geom_tile(aes(fill=accrued_payoffs)))
				dev.off()
			}
		}
		rm(d)
	}
	print("Made figures.")
	rm(df)
}

files = c("/Users/jg1g12/Downloads/1_women_sharing_women_%s.db", "/Users/jg1g12/Downloads/2_women_sharing_women_%s.db", "/Users/jg1g12/Downloads/3_women_sharing_women_%s.db")
cols = "player_type, accrued_payoffs, referred, hash"
for(x in files) {
	df <- sqldf(sprintf("select %s from results where num_rounds>0 OR referred=1", cols), dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, decision_rule_responder, game, women_1, women_2, hash from parameters", dbname=sprintf(x, 1))
	print("Loaded 1..")
	for(i in 2:16) {
		df = rbind(df, sqldf(sprintf("select %s from results", cols), dbname=sprintf(x, i)))
		params = rbind(params, sqldf("select decision_rule_signaller, decision_rule_responder, game, women_1, women_2, hash from parameters", dbname=sprintf(x, i)))
		print(sprintf("Loaded %d - %s.", i, sprintf(x, i)))
	}
	#df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	df <- aggregate(df, by=list(Group.women_1=df$women_1, Group.women_2=df$women_2, Group.game=df$game, Group.decision_rule_signaller=df$decision_rule_signaller, Group.decision_rule_responder=df$decision_rule_responder, Group.player_type=df$player_type), FUN=mean)
	for(i in unique(interaction(df$Group.game, df$Group.decision_rule_signaller, df$Group.decision_rule_responder))) {
		d <- subset(df, interaction(df$Group.game, df$Group.decision_rule_signaller, df$Group.decision_rule_responder) == i)
		c <- ggplot(d, aes(x=women_1, y=women_2))
				png(sprintf("../figures/payoffs_%s_%s_%s_women.png", as.character(d$Group.decision_rule_signaller)[1], as.character(d$Group.decision_rule_responder)[1], as.character(d$Group.game)[1], i))
				print(c + geom_tile(aes(fill=accrued_payoffs)))
				dev.off()
		for(k in 0:2) {
					png(sprintf("../figures/honest_signals_%s_%s_%s_type_%d_women.png", as.character(d$Group.decision_rule_signaller)[1], as.character(d$Group.decision_rule_responder)[1], as.character(d$Group.game)[1], j))
					signal = eval(parse(text=sprintf("d$signal_%d_frequency", j)))
					print(c + geom_tile(aes(fill=signal)))
					dev.off()
				}
		for(j in 0:2) {
			typed = subset(d, d$Group.player_type == j)
			if(nrow(typed) > 0) {
				c <- ggplot(typed, aes(x=women_1, y=women_2))
				png(sprintf("../figures/payoffs_%s_%s_%s_type_%d.png", as.character(d$Group.decision_rule_signaller)[1], as.character(d$Group.decision_rule_responder)[1], as.character(d$Group.game)[1], j))
				print(c + geom_tile(aes(fill=accrued_payoffs)))
				dev.off()
			}
		}
		rm(d)
	}
	print("Made figures.")
	rm(df)
}