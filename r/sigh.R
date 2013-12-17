require(ggplot2)
require(sqldf)

num_rounds_type <- function(df, type, x, y) {
	# Average number of rounds played
	x = eval(parse(text=sprint("df$%s",x)))
	y = eval(parse(text=sprint("df$%s",y)))
	fill = eval(parse(text=sprintf("df$rounds_played_type_%d", type)))
	filter = eval(parse(text=sprintf("df$type_%d_finished", type)))
	df <- subset(df, filter > 0)
	df <- aggregate(df, by=list(x, y), FUN=mean)
	c <- ggplot(df, aes(x=x, y=y))
	return(c + geom_tile(aes(fill=fill)))
}

payoffs_type <- function(df, type, x, y) {
	# Average payoff accrued
	x = eval(parse(text=sprint("df$%s",x)))
	y = eval(parse(text=sprint("df$%s",y)))
	fill = eval(parse(text=sprintf("df$accrued_payoffs_type_%d", type)))
	#filter = eval(parse(text=sprintf("df$type_%d_finished", type)))
	#df <- subset(df, filter > 0)
	df <- aggregate(df, by=list(x, y), FUN=mean)
	c <- ggplot(df, aes(x=x, y=y))
	return(c + geom_tile(aes(fill=fill)))
}

num_rounds <- function(df) {
	# Average number of rounds played over time for all types
	# Include only rounds where at least some of that type finished
	# Type 0
	s <- subset(df, df$type_0_finished > 0)
	d$appointment <- s['appointment']
	d$num_rounds <- s['rounds_played_type_0']
	d$player_type <- "Light"
	# Type 1
	s <- subset(df, df$type_1_finished > 0)
	e$appointment <- s['appointment']
	e$num_rounds <- s['rounds_played_type_1']
	e$player_type <- "Moderate"
	d <- rbind(d, e)
	# Type 2
	s <- subset(df, df$type_2_finished > 0)
	e$appointment <- s['appointment']
	e$num_rounds <- s['rounds_played_type_2']
	e$player_type <- "Heavy"
	d <- rbind(d, e)
	
	c <- ggplot(d, aes(x=appointment, y=num_rounds, color=player_type)) + xlab("Appointment") + ylab("Rounds played")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=player_type))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Type")
	return(c)
}

signals_by_type <- function(df, type) {
	frame_type = paste(paste("df$type", type, sep="_"), "signal", sep="_")
	a = paste(frame_type, 0, sep="_")
	b = paste(frame_type, 1, sep="_")
	c = paste(frame_type, 2, sep="_")
	y <- c(eval(parse(text=a)), eval(parse(text=b)), eval(parse(text=c)))
	d <- data.frame(y)
	d$x <- rep(min(df$appointment):max(df$appointment), nrow(d) / (max(df$appointment) + 1))
	d$group <- c(rep("Light", nrow(d)/3), rep("Moderate", nrow(d)/3), rep("Heavy", nrow(d)/3))
	c <- ggplot(d, aes(x=x, y=y, color=group)) + xlab("Appointment") + ylab("Signal frequency")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Signal") + ylim(0.0, 1.0)
	return(c)
}

load <- function(x) {
	df <- sqldf("select * from results", dbname=x)
	params <- sqldf("select * from parameters", dbname=x)
	df <- merge(x=df, y=params, by.x="hash", by.y="hash", all.x=TRUE)
	print(sprintf("Loaded %s", x))
	return(df)
}

files = c("/Users/user/Downloads/1_women_proportions_women.db", "/Users/user/Downloads/2_women_proportions_women.db", "/Users/user/Downloads/3_women_proportions_women.db")
for(x in files) {
	df <- load(x)
	#df <- aggregate(df, by=list(df$women_1, df$women_2, df$game, df$decision_rule_signaller, df$decision_rule_responder, df$player_type), FUN=mean)
	#df$accrued_payoffs = (df$accrued_payoffs - min(df$accrued_payoffs)) / (max(df$accrued_payoffs) - min(df$accrued_payoffs))
	print("Merged.")
	for(i in unique(interaction(df$game, df$Group.4, df$Group.5, df$Group.6))) {
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