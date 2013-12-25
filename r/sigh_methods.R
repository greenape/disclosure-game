require(sqldf)
require(ggplot2)

num_rounds_type <- function(df, type, x, y, file) {
    df = eval(parse(text=sprintf("subset(df, df$type_%d_finished > 0)", type)))
    #df <- subset(df, filter > 0)
    # Average number of rounds played
    x = eval(parse(text=sprintf("df$%s",x)))
    y = eval(parse(text=sprintf("df$%s",y)))
    fill = eval(parse(text=sprintf("df$rounds_played_type_%d", type)))
    data$x = data.frame(x)
    data$y = data.frame(y)
    data$fill = data.frame(fill)
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(data, aes(x=x, y=y))
    png(file)
    print(c + geom_tile(aes(fill=fill)))
    dev.off()
}

payoffs_type <- function(df, type, x, y) {
    # Average payoff accrued
    df = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    #df <- subset(df, filter > 0)
    x = eval(parse(text=sprintf("df$%s",x)))
    y = eval(parse(text=sprintf("df$%s",y)))
    fill = eval(parse(text=sprintf("df$accrued_payoffs_type_%d", type)))
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(df, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}

signals_type <- function(df, type, signal, x, y) {
    # Levelplot of average signal frequency across whole game
    # Include only rounds where at least some of that type played
    # Type 0
    df = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    #df <- subset(df, filter > 0)
    # Average payoff accrued
    x = eval(parse(text=sprintf("df$%s",x)))
    y = eval(parse(text=sprintf("df$%s",y)))
    fill = eval(parse(text=sprintf("df$type_%d_signal_%d", type, signal)))
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(df, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}

honesty_type <- function(df, type, x, y) {
    # Levelplot of normalised average absolute signal distance.
    # Include only rounds where at least some of that type played
    # Type 0
    df = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    #df <- subset(df, filter > 0)
    # Average payoff accrued
    x = eval(parse(text=sprintf("df$%s",x)))
    y = eval(parse(text=sprintf("df$%s",y)))
    for(signal in 0:2) {
         fill = eval(parse(text=sprintf("df$type_%d_signal_%d", type, signal)))
    }
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(df, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}


load <- function(x) {
    df <- sqldf("select * from results", dbname=x)
    params <- sqldf("select * from parameters", dbname=x)
    df <- merge(x=df, y=params, by.x="hash", by.y="hash", all.x=TRUE)
    print(sprintf("Loaded %s", x))
    return(df)
}

num_rounds <- function(df) {
    # Average number of rounds played over time for all types
    # Include only rounds where at least some of that type finished
    # Type 0
    s <- subset(df, df$type_0_finished > 0)
    appointment <- data.frame(s['appointment'])
    num_rounds <- data.frame(s['rounds_played_type_0'])
    d <- merge(appointment, num_rounds)
    d$player_type <- "Light"
    print("Light.")
    # Type 1
    s <- subset(df, df$type_1_finished > 0)
    appointment <- data.frame(s['appointment'])
    num_rounds <- data.frame(s['rounds_played_type_1'])
    e <- merge(appointment, num_rounds)
    e$player_type <- "Moderate"
    d <- rbind(d, e)
    print("Mod.")
    rm(e)
    # Type 2
    s <- subset(df, df$type_2_finished > 0)
    appointment <- data.frame(s['appointment'])
    num_rounds <- data.frame(s['rounds_played_type_2'])
    e <- merge(appointment, num_rounds)
    e$player_type <- "Heavy"
    d <- rbind(d, e)
    print("High.")
    
    c <- ggplot(d, aes(x=appointment, y=num_rounds, color=player_type)) + xlab("Appointment") + ylab("Rounds played")
    c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=player_type))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Type")
    return(c)
}

signals_by_type <- function(df, type) {
    # Include only rounds where at least some of that type played
    # Type 0
    df = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    #df <- subset(df, filter > 0)
    frame_type = paste(paste("df$type", type, sep="_"), "signal", sep="_")
    a = paste(frame_type, 0, sep="_")
    b = paste(frame_type, 1, sep="_")
    c = paste(frame_type, 2, sep="_")
    d$appointment <- s['appointment']
    d$num_rounds <- s[a]
    d$player_type <- "Light"
    # Type 1
    s <- subset(df, df$type_1_finished > 0)
    e$appointment <- s['appointment']
    e$num_rounds <- s[b]
    e$player_type <- "Moderate"
    d <- rbind(d, e)
    # Type 2
    s <- subset(df, df$type_2_finished > 0)
    e$appointment <- s['appointment']
    e$num_rounds <- s[c]
    e$player_type <- "Heavy"
    d <- rbind(d, e)
    
    c <- ggplot(d, aes(x=appointment, y=num_rounds, color=player_type)) + xlab("Appointment") + ylab("Signal frequency")
    c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=player_type))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Signal")
    return(c)
}

load <- function(x) {
    df <- sqldf("select * from results where appointment > 500", dbname=x)
    params <- sqldf("select * from parameters", dbname=x)
    df <- merge(x=df, y=params, by.x="hash", by.y="hash", all.x=TRUE)
    print(sprintf("Loaded %s", x))
    return(df)
}