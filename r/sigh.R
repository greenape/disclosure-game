require(ggplot2)
require(sqldf)

load <- function(x) {
df <- sqldf("select player_type, signal_0_frequency, signal_1_frequency, signal_2_frequency, accrued_payoffs, type_2_frequency, type_1_frequency, hash from results", dbname=sprintf(x, 1))
	params <- sqldf("select decision_rule_signaller, decision_rule_responder, game, women_1, women_2, hash from parameters", dbname=sprintf(x, 1))
	print("Loaded 1..")
	for(i in 2:16) {
		df = rbind(df, sqldf("select player_type, signal_0_frequency, signal_1_frequency, signal_2_frequency, accrued_payoffs, type_2_frequency, type_1_frequency, hash from results", dbname=sprintf(x, i)))
		params = rbind(params, sqldf("select decision_rule_signaller, decision_rule_responder, game, women_1, women_2, hash from parameters", dbname=sprintf(x, i)))
		print(sprintf("Loaded %d - %s.", i, sprintf(x, i)))
	}
	df <- merge(x=df, y=unique(params), by.x="hash", by.y="hash", all.x=TRUE)
	return(df)
}

files = c("/Users/user/Downloads/1_women_proportions_women_%s.db", "/Users/user/Downloads/2_women_proportions_women_%s.db", "/Users/user/Downloads/3_women_proportions_women_%s.db")
for(x in files) {
	df <- load(x)
	df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
	df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
	print("Merged.")
	for(i in unique(interaction(df$Group.3, df$Group.4, df$Group.5, df$Group.6))) {
			d <- subset(df, interaction(df$Group.3, df$Group.4, df$Group.5, df$Group.6) == i)
			c <- ggplot(d, aes(x=Group.1, y=Group.2))

			png(sprintf("../figures/honest_signals_%s_%s_%s_type_%d_women.png", as.character(d$Group.3)[1], as.character(d$Group.4)[1], as.character(d$Group.3)[1], d$Group.6))
			signal = eval(sprintf("d$signal_%d_frequency", d$Group.6[1]))
			print(c + geom_tile(aes(fill=signal)))
			dev.off()
			rm(d)
	}
	print("Made figures.")
	rm(df)
}