library(sqldf)

get_max_type <- function(climb) {
  trim <- function (x) gsub("^\\s+|\\s+$", "", x)
  
  equip_type = c('boulder','trad','sport','tr')
  
  # UNSPEAKABLE CODE to get one column describing the type
  max_type = unlist(apply(climb, 1, function(route) {
    type_iter = lapply(equip_type, function(t) {
      silly = as.logical(trim(route[t]))
      if (silly) {
        return(t)
      } else {
        return(NULL)
      }
    })
    type = max(unlist(type_iter))
    if (is.null(type)) { type = NA }
    return(type)
  }))
  max_type[max_type=="-Inf"] <- NA
  return(max_type)
}
get_fa_date <- function(fa_string) {
  
  match = gregexpr('[0-9][0-9][0-9][0-9]', fa_string, perl = TRUE)[[1]]
  start_position = match[[1]]
  if(!is.na(start_position) && start_position > -1) {
    gofor = attr(match, 'match.length')
    year_digits = substr(fa_string, start_position, start_position+gofor)
    # year = as.Date(year_digits, format = '%Y')
    year = as.integer(year_digits)
    return(year)
  } else {
    return(NA)
  }
}

my.pwd = '~/RouteRobot/cluster/'

# copied data here after running /scraping/driver.py
d <- read.csv("~/RouteRobot/cluster/climb.csv", row.names=1, stringsAsFactors=FALSE)

# good analysis starts with a good schema
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
  ice = unlist(lapply(d$ice,is.na)), # TODO cast aid, mixed, ice, alpine
  mixed = unlist(lapply(d$mixed,is.na)),
  aid = unlist(lapply(d$aid,is.na)),
  alpine = unlist(lapply(d$alpine,is.na)),
  trad = as.logical(d$trad),
  sport = as.logical(d$sport),
  boulder = as.logical(d$boulder),
  tr = as.logical(d$tr),
  chipped = as.logical(d$chipped),
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

# shitty code to get an approximate grouping
climb$max_type = get_max_type(climb)

# more bad code to grab first ascent year
climb$fa_date = sapply(as.character(climb$fa), get_fa_date)


source(paste0(my.pwd,'viz.R'))
print(first_ascent_timeline(climb))
print(YDS_histogram(climb))
print(Hueco_histogram(climb))
print(trend_scatter(
  climb, x_string = 'page_views', y_string = 'staraverage',
  log_scale = TRUE
))
print(trend_scatter(
  climb, x_string = 'feet', y_string = 'staraverage',
  log_scale = TRUE, limits = c(5,2000)
))
print(trend_scatter(
  climb, x_string = 'grade', y_string = 'staraverage'
))
