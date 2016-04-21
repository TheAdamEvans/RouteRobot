library(sqldf)
d <- read.csv("~/RouteRobot/cluster/climb.csv", row.names=1, stringsAsFactors=FALSE)

climb = data.frame(
  href = as.character(d$href),
  nickname = as.character(d$nickname),
  is_route = as.logical(d$is_route),
  is_area = as.logical(d$is_area),
  feet = as.numeric(d$feet),
  page_views = as.numeric(d$page_views),
  pitches = as.numeric(d$pitches),
  protect_rate = as.character(d$protect_rate),
  commitment = as.character(d$commitment),
  boulder = as.logical(d$boulder),
  sport = as.logical(d$sport),
  trad = as.logical(d$trad),
  tr = as.logical(d$tr),
  aid = as.logical(d$aid),
  alpine = as.logical(d$alpine),
  chipped = as.logical(d$chipped),
  ice = as.logical(d$ice),
  mixed = as.logical(d$mixed),
  grade = as.numeric(d$grade),
  rateHueco = as.character(d$rateHueco),
  rateYDS = as.character(d$rateYDS),
  rateFloatHueco = as.numeric(d$rateFloatHueco),
  ratePCTHueco = as.numeric(d$ratePCTHueco),
  rateFloatYDS = as.numeric(d$rateFloatYDS),
  ratePCTYDS = as.numeric(d$ratePCTYDS),
  staraverage = as.numeric(d$staraverage),
  starvotes = as.numeric(d$starvotes),
  name = as.character(d$name),
  elevation = as.character(d$elevation),
  season = as.character(d$season),
  fa = as.character(d$fa)
)


plot_YDS_histogram <- function(climb){
  # filter to only routes
  climb = climb[climb$is_route,]
  
  # most climbs are between 5.5 and 5.14
  grade_breaks = seq(5, 14.5, by = 0.5)
  # magic number math to make pretty labels
  grd = rep(4:13, each = 2)
  adj = rep(c('','+'), 10)
  grade_labels = paste0('5.',grd, adj)
  names(grade_breaks) = grade_labels
  
  # compare YDS rate to pretty grades and return name of closest one
  climb$clean_label = unlist(lapply(
    climb$rateFloatYDSRound, function(g) {
      label = grade_labels[which.min(abs(grade_breaks - g))]
      if (length(label) > 0) {
       return(label) 
      } else { return("") }
    }
  ))
  
  # count how many climbs fall into each grade
  grade_histo = sqldf("
  select
    clean_label,
    count(distinct href) num_climbs,
    avg(rateFloatYDS) hard
  from climb
  where rateYDS not in ('')
  group by clean_label
  order by hard
        ")
  # classic reorder for bar plot
  grade_histo$clean_label = reorder(grade_histo$clean_label, grade_histo$hard)
  
  # plot count frequency versus difficulty
  plt = ggplot(data=grade_histo)
  plt = plt + geom_bar(stat='identity', aes(x = clean_label, y = num_climbs)) +
  plt = plt + labs(title="Climbs are Most Often 5.10")
  plt = plt + labs(x="Difficulty", y="Number of Climbs")
  
  return(plt)
}
