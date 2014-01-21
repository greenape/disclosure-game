require(sqldf)
require(ggplot2)

num_rounds_type <- function(df, type, x, y) {
    s = eval(parse(text=sprintf("subset(df, df$type_%d_finished > 0)", type)))
    #df <- subset(df, filter > 0)
    # Average number of rounds played
    #x = eval(parse(text=sprintf("df$%s",x)))
    #y = eval(parse(text=sprintf("df$%s",y)))
    fill = sprintf("rounds_played_type_%d", type)
    z = data.frame(s[c(x,y,fill)])
    names(z)[names(z)==x] <- "x"
    names(z)[names(z)==y] <- "y"
    names(z)[names(z)==fill] <- "fill"
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(z, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}

payoffs_type <- function(df, type, x, y) {
    # Average payoff accrued
    s = eval(parse(text=sprintf("subset(df, df$type_%d_finished > 0)", type)))
    #df <- subset(df, filter > 0)
    fill = sprintf("accrued_payoffs_type_%d", type)
    z = data.frame(s[c(x,y,fill)])
    names(z)[names(z)==x] <- "x"
    names(z)[names(z)==y] <- "y"
    names(z)[names(z)==fill] <- "fill"
    #fill = eval(parse(text=sprintf("df$accrued_payoffs_type_%d", type)))
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(z, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}

signals_type <- function(df, type, signal, x, y) {
    # Levelplot of average signal frequency across whole game
    # Include only rounds where at least some of that type played
    # Type 0
    #s = eval(parse(text=sprintf("subset(df, df$type_%d_frequency > 0)", type)))
    s <- df
    #df <- subset(df, filter > 0)
    # Average payoff accrued
    fill = sprintf("type_%d_signal_%d", type, signal)
    z = data.frame(s[c(x,y,fill)])
    names(z)[names(z)==x] <- "x"
    names(z)[names(z)==y] <- "y"
    names(z)[names(z)==fill] <- "fill"
    #fill = eval(parse(text=sprintf("df$type_%d_signal_%d", type, signal)))
    #df <- aggregate(df, by=list(x, y), FUN=mean)
    c <- ggplot(z, aes(x=x, y=y))
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
    d <- data.frame(s[c('appointment','rounds_played_type_0')])
    names(d)[names(d)=="rounds_played_type_0"] <- "num_rounds"
    d$player_type <- "Light"
    print("Light.")
    # Type 1
    s <- subset(df, df$type_1_finished > 0)
    e <- data.frame(s[c('appointment', 'rounds_played_type_1')])
    e$player_type <- "Moderate"
    names(e)[names(e)=="rounds_played_type_1"] <- "num_rounds"
    d <- rbind(d, e)
    print("Mod.")
    rm(e)
    # Type 2
    s <- subset(df, df$type_2_finished > 0)
    e <- data.frame(s[c('appointment', 'rounds_played_type_2')])
    e$player_type <- "Heavy"
    names(e)[names(e)=="rounds_played_type_2"] <- "num_rounds"
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
    data = "type_%d_signal_%d"
    a = sprintf(data, type, 0)
    b = sprintf(data, type, 1)
    c = sprintf(data, type, 2)
    d <- data.frame(s[c('appointment', a)])
    d$signal <- "Light"
    names(d)[names(d)==a] <- "frequency"
    # Type 1
    e <- data.frame(s[c('appointment', b)])
    e$signal <- "Moderate"
    names(e)[names(e)==b] <- "frequency"
    d <- rbind(d, e)
    # Type 2
    e <- data.frame(s[c('appointment', c)])
    e$signal <- "Heavy"
    names(e)[names(e)==c] <- "frequency"
    d <- rbind(d, e)
    
    c <- ggplot(d, aes(x=appointment, y=frequency, color=signal)) + xlab("Appointment") + ylab("Signal frequency")
    c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=signal))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Signal")
    return(c)
}

load <- function(x) {
    df <- sqldf("select * from results", dbname=x)
    params <- sqldf("select * from parameters", dbname=x)
    df <- merge(x=df, y=params, by.x="hash", by.y="hash", all.x=TRUE)
    print(sprintf("Loaded %s", x))
    return(df)
}