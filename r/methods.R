require(ggplot2)

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

signals_imply_referral_by_type <- function(df, type) {
	frame_type = paste(paste("df$type", type, sep="_"), "signal", sep="_")
	a = paste(frame_type, 0, sep="_")
	a = paste(a, "means_referral", sep="_")
	b = paste(frame_type, 1, sep="_")
	b = paste(b, "means_referral", sep="_")
	c = paste(frame_type, 2, sep="_")
	c = paste(c, "means_referral", sep="_")
	y <- c(eval(parse(text=a)), eval(parse(text=b)), eval(parse(text=c)))
	d <- data.frame(y)
	d$x <- rep(min(df$appointment):max(df$appointment), nrow(d) / max(df$appointment))
	d$group <- c(rep("Light", nrow(d)/3), rep("Moderate", nrow(d)/3), rep("Heavy", nrow(d)/3))
	c <- ggplot(d, aes(x=x, y=y, color=group)) + xlab("Appointment") + ylab("Strength")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Signal") + ylim(0.0, 1.0)
	return(c)
}

finished_by_type <- function(df) {
	frame_type = "df$type"
	a = paste(frame_type, 0, sep="_")
	a = paste(a, "finished", sep="_")
	b = paste(frame_type, 1, sep="_")
	b = paste(b, "finished", sep="_")
	c = paste(frame_type, 2, sep="_")
	c = paste(c, "finished", sep="_")
	y <- c(eval(parse(text=a)), eval(parse(text=b)), eval(parse(text=c)))
	d <- data.frame(y)
	d$x <- rep(min(df$appointment):max(df$appointment), nrow(d) / max(df$appointment))
	d$group <- c(rep("Light", nrow(d)/3), rep("Moderate", nrow(d)/3), rep("Heavy", nrow(d)/3))
	c <- ggplot(d, aes(x=x, y=y, color=group)) + xlab("Appointment") + ylab("Percent referred")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Type") + ylim(0.0, 1.0)
	return(c)
}

referred_by_type <- function(df) {
	frame_type = "df$type"
	a = paste(frame_type, 0, sep="_")
	a = paste(a, "ref", sep="_")
	b = paste(frame_type, 1, sep="_")
	b = paste(b, "ref", sep="_")
	c = paste(frame_type, 2, sep="_")
	c = paste(c, "ref", sep="_")
	y <- c(eval(parse(text=a)), eval(parse(text=b)), eval(parse(text=c)))
	d <- data.frame(y)
	d$x <- rep(min(df$appointment):max(df$appointment), nrow(d) / max(df$appointment))
	d$group <- c(rep("Light", nrow(d)/3), rep("Moderate", nrow(d)/3), rep("Heavy", nrow(d)/3))
	c <- ggplot(d, aes(x=x, y=y, color=group)) + xlab("Appointment") + ylab("Percent referred")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Type") + ylim(0.0, 1.0)
	return(c)
}

distributions <- function(df) {
	frame_type = "df$global_type_frequency_%d"
	a <- sprintf(frame_type, 0)
	b <- sprintf(frame_type, 1)
	c <- sprintf(frame_type, 2)
	y <- c(eval(parse(text=a)), eval(parse(text=b)), eval(parse(text=c)))
	d <- data.frame(y)
	d$x <- rep(min(df$appointment):max(df$appointment), nrow(d) / max(df$appointment))
	d$group <- c(rep("Low", nrow(d)/3), rep("Moderate", nrow(d)/3), rep("Harsh", nrow(d)/3))
	c <- ggplot(d, aes(x=x, y=y, color=group)) + xlab("Appointment") + ylab("Percent referred")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Type") + ylim(0.0, 1.0)
	return(c)
}

distributions_by_type <- function(df, player_type) {
	frame_type = "df$player_type_%d_frequency_%d"
	a <- sprintf(frame_type, player_type, 0)
	b <- sprintf(frame_type, player_type, 1)
	c <- sprintf(frame_type, player_type, 2)
	y <- c(eval(parse(text=a)), eval(parse(text=b)), eval(parse(text=c)))
	d <- data.frame(y)
	d$x <- rep(min(df$appointment):max(df$appointment), nrow(d) / max(df$appointment))
	d$group <- c(rep("Low", nrow(d)/3), rep("Moderate", nrow(d)/3), rep("Harsh", nrow(d)/3))
	c <- ggplot(d, aes(x=x, y=y, color=group)) + xlab("Appointment") + ylab("Percent referred")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Type") + ylim(0.0, 1.0)
	return(c)
}
