# text_templates = {
# 	1: '#{custom1} #{custom2} #{custom3}',

# 	2: '2018년 6월 13일 오전 7시부터 제7대 전국동시지방선거가 막을 열었다. 오후 6시를 기준으로 투표가 마감되었고, 최종 집계된 투표율은 {toorate_avg_nat}%로 나타났다.',

# 	3: '이번 지방선거의 투표율은 지난 선거에 비해 {current_toorate_past_toorate}%p {toorate_compare} 것으로, {toorate_compare_add}. 전국에서 가장 투표율이 높은 지역은 {toorate_rank1}이며, 그 뒤를 {toorate_rank}{josa} 뒤따르고 있다.',
# 	# 투표진행중일때는?

# 	4: '{region1} 지역 전체의 투표율은 {toorate_region1}%로 전국 평균보다 약 {toorate_region1_toorate_avg_nat}% 포인트 {toorate_compare1} 수치이며, {region2}는 {toorate_region2}%로 전국 평균보다 약간 {toorate_compare2} 투표율을 보였다.',

# 	5: '{hour} 현재 전국 평균 개표율은 {openrate_avg_nat}%이며, 서울은 {openrate_seoul}%, 경기도는 {openrate_gyeonggi}%의 개표 진행 상황을 보이고 있다.',

# 	6: '{hour} 현재 전국에서 가장 개표가 빠른 지역은 {openrate_sunname1_rank1}이며, 시군구 단위에서 개표가 가장 빠른 곳은 {openrate_sunname2_rank1}로 {openrate_sunname2_rank1_rate}%의 개표율을 보이고 있다.',

# 	7: '{hour} 현재 {region1} 지역 전체의 개표율은 {openrate_region1}%로 {region1_exception} {region2}는 {openrate_region2}%로 {region2_exception}',
# 	'7-0': '아직 개표가 시작되지 않았다.',
# 	'7-1': '전국 평균보다 약 {openrate_region1_openrate_avg_nat}% 포인트 {compare_region1} 수치이며,',
# 	'7-2': '전국 평균보다 {compare_region2} 개표율을 보였다.',

# 	8: '{hour} 현재 총 {num}개의 지방자치단체장 및 지방자치 의원을 선출하는 이번 지방 선거에서 {rank1_party}은 {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {rank2_party}({rank2_party_num}개), {rank3_party}({rank3_party_num}개){josa} 잇고 있다.',

# 	9: '{hour} 현재 전국 {num}개의 시/도지사 선거에서 {rank1_party}은 {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {rank2_party}({rank2_party_num}개), {rank3_party}({rank3_party_num}개){josa} 잇고 있다.',

# 	10: '{hour} 현재 {region1}{sido_type} 선거에서는 {openrate_region1}%의 개표율을 보이는 가운데 {region1_rank1_party} {region1_rank1_candidate} 후보가 {region1_rank1_pollrate}%의 득표율로 1위, {region1_rank2_party} {region1_rank2_candidate} 후보가 {region1_rank2_pollrate}%의 득표율로 2위를 달리고 있다.',

# 	11: '{hour} 현재 {region2}{sido_type} 선거에서는 {openrate_region2}%의 개표율을 보이는 가운데 {region2_rank1_party} {region2_rank1_candidate} 후보가 {region2_rank1_pollrate}%의 득표율로 1위, {region2_rank2_party} {region2_rank2_candidate} 후보가 {region2_rank2_pollrate}%의 득표율로 2위를 달리고 있다.',
# }

# seq2type = {
# 	1:'cover', # 표지
# 	2:'rate', # 투표율 일반
# 	3:'map', # 투표율 비교 / 전국
# 	4:'map', # 투표율 개인화 / 지역
# 	5:'rate', # 개표율 일빈
# 	6:'map', # 개표율 비교 / 전국
# 	7:'map', # 개표율 개인화 / 지역
# 	8:'winner', # 득표율 일반 
# 	9:'graph', # 득표율 개인화(선거유형) / (정당, 1위개수)
# 	10:'graph', # 득표율 개인화(지역1) / (후보, 개표율)
# 	11:'graph', # 득표율 개인화(지역2) / (후보, 개표율)
# }
# 
text_templates = {
	1: '#{custom1} #{custom2} #{custom3}',

	### 투표율
	2: '13일 오전 6시를 기해 시작된 제7회 전국동시지방선거가 오후 6시에 모두 마무리되었다. 이번 선거의 전국 최종 투표율은 {toorate_avg_nat}%로 집계되었다.',
	
	'2-1': '제7회 전국동시지방선거가 13일 오전 6시를 기해 전국의 (수치 미정)개 투표소에 시작되었으며, {hour} 현재 전국 투표율은 {toorate_avg_nat}%로 집계되었다.', # 투표중

	3: '이는 2014년 6회 지방선거의 최종 투표율 {past_toorate}%보다 {current_toorate_past_toorate}%포인트 {toorate_compare} 수치다. 전국에서 투표율이 가장 높은 지역은 {toorate_rank1}이며, {toorate_rank}{josa} 그 뒤를 이었다.',

	'3-1': '이는 2014년 6회 지방선거의 같은 시간대 투표율 {past_toorate}%보다 {current_toorate_past_toorate}%포인트 {toorate_compare} 수치다. 이 시간까지 전국에서 투표율이 가장 높은 지역은 {toorate_rank1}이며, {toorate_rank}{josa} 그 뒤를 따르고 있다.', # 투표중

	4: '{region1}의 투표율은 {toorate_region1}%로 전국 평균보다 {toorate_region1_toorate_avg_nat}% 포인트 {toorate_compare1} 수치이다. 또한, {region2}{josa} {toorate_region2}%를 기록하며 전국 평균보다 {toorate_region2_toorate_avg_nat}% 포인트 {toorate_compare2} 투표율을 보였다.', # region2 전국평균 = region1 전국평균 ?

	'4-1': '{region1}의 투표율은 {toorate_region1}%로 전국 평균보다 {toorate_region1_toorate_avg_nat}% 포인트 {toorate_compare1} 수치이다. 또한, {region2}{josa} {toorate_region2}%를 기록하며 전국 평균보다 {toorate_region2_toorate_avg_nat}%포인트 {toorate_compare2} 투표율을 보이고 있다.', # 투표중

	5: '{candidate} 후보가 속해 있는 {candidate_region}의 최종 투표율은 {candidate_region_toorate}%를 기록했다.',

	'5-1': '{candidate} 후보가 속해 있는 {candidate_region}의 투표율은 {hour} 현재 {candidate_region_toorate}%를 기록하고 있다.', # 투표중

	6: '투표율 특이사항',

	### 개표율
	7: '{hour} 현재 제7회 지방선거 개표는 전국 (선거구 수)개소에서 진행중이며 개표율은 전국 평균 {openrate_avg_nat}%이다. 개표는 이전 선거 동일 시간보다 {openrate_compare} 속도로 진행되고 있다. 따라서 이전 선거에 비해 {openrate_compare_plus} 시간에 선거 결과가 나타날 것으로 보인다.',

	8: '{hour} 현재 시도지사 선거에서 가장 개표가 빠른 지역은 {openrate_sunname1_rank1}으로 {openrate_sunname1_rank1_rate}%의 개표율을 보이고 있으며, {openrate_sunname1_rank2} 지역이 {openrate_sunname1_rank2_rate}%로 뒤따르고 있다.',

	9: '{hour} 현재 시군구청장 선거에서 {openrate_sunname2_rank1} 지역이 {openrate_sunname2_rank1_rate}%로 개표가 가장 빠르게 이루어지고 있으며, {openrate_sunname2_rank2} 지역이 {openrate_sunname2_rank2_rate}%의 개표율로 그 뒤을 잇고 있다.',

	10: '{hour} 현재 {region1} 지역 전체의 개표율은 {openrate_region1}%로 전국 평균보다 약 {openrate_region1_openrate_avg_nat}% 포인트 {compare_region1} 수치이다. {region1} 지역에서 개표가 가장 빠른 곳은 {openrate_region1_region2_rank1}{josa1} {openrate_region1_region2_rank1_rate}%의 개표율을 보이고 있다. {region2}{josa2} {openrate_region2}%로 전국 평균보다 {compare_region2} 개표율을 보이고 있다.', 

	'10-1': '{hour} 현재 {region1} 지역은 아직 개표가 시작되지 않았다.', # 개표율 = 0

	11: '전국 {poll_num_sunname}개의 {poll} 선거에서 개표율 1위를 달리고 있는 {poll_openrate_rank1} 지역은 {poll_openrate_rank1_rate}%의 개표율을 보이고 있다. 그 뒤를 {poll_openrate_rank2} 지역이 {poll_openrate_rank1_rate}%로 따르고 있다. {poll} 선거의 전국 평균 개표율은 {poll_openrate_nat_avg}%이다.',

	'11-1': '{hour} 현재 {poll}{josa} 아직 개표가 시작되지 않았다.',

	12: '{candidate} 후보가 속해 있는 {candidate_region} 지역의 {candidate_poll} 선거 개표율은 {candidate_poll_openrate}%이다.',

	'12-1': '{candidate} 후보가 속해 있는 {candidate_region} 지역의 {candidate_poll} 선거는 아직 개표가 시작되지 않았다.',

	13: '개표율 특이사항',

	### 득표율
	14: '{hour} 현재 제 7회 지방선거 개표가 진행중인 가운데, {rank1_party}{josa} 우세한 것으로 나타났다.',

	15: '{hour} 현재 전국 (시도지사 선거구 수)개의 시·도지사 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {ranks_party}{josa2} 잇고 있다.',

	16: '{hour} 현재 총 (지방자치단체 선거구 수)개의 시군구청장을 선출하는 이번 지방선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {ranks_party}{josa2} 잇고 있다.',

	17: '{hour} 현재 {region1}{region1_poll} 선거에서는 {region1_openrate}%의 개표율을 보이는 가운데 {region1_rank1_party} {region1_rank1_name} 후보가 {region1_rank1_rate}%의 득표율로 1위, {region1_rank2_party} {region1_rank2_name} 후보가 {region1_rank2_rate}%의 득표율로 2위를 달리고 있다.',

	'17-1': '{region1}{region1_poll} 선거에서 {region1_rank1_party} {region1_rank1_name} 후보가 {region1_rank1_rate}%의 득표율로 당선이 확정되었으며, {region1_rank2_party} {region1_rank2_name} 후보가 {region1_rank2_rate}%의 득표율로 2위를 기록했다.',

	18: '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region} 지역의 {candidate_poll} 선거에서는 {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 1위, {candidate_poll_rank2_name} 후보가 {candidate_poll_rank2_rate}%의 득표율로 2위를 달리고 있다.',

	'18-1': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region} 지역의 {candidate_poll} 선거에서는 {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 당선이 확정되었다.',

	## 선거구수.관심정당1.시도지사.1위, 관심정당1.시도지사.순위 
	19: '{관심정당1}은 시도지사 선거에서 총 17개 선거구 중 {선거구수.관심정당1.시도지사.1위}개의 선거구에서 득표율 {관심정당1.시도지사.순위}위를 달리고 있다. 시군구청장 선거에서는 총 226개 선거구 중  {선거구수.관심정당1.시군구청장.1위}개의 선거구에서 득표율 {관심정당1.시도지사.순위}위를 달리고 있다.',

	'19-1': '{관심정당1}은 시도지사선거에서 총 17개 선거구 중 {선거구수.관심정당1.시도지사.1위.당선확정}명의 후보의 당선이 확정되었다. 시군구청장 선거에서는 총 226개의 선거구 중 {선거구수.관심정당1.시군구청장.1위.당선확정}명의 후보의 당선이 확정되었다.',

	20: '득표율 특이사항',

	21: '{hour} 현재 모든 선거구에서의 개표가 완료되고 총 17명의 시도지사, 226명의 구시군의장, 824명의 광역의원, 2927명의 지역의원의 당선이 확정되었다. 또한 17명의 교육감과 5명의 교육의원의 당선이 확정되었다.',

	22: '이번 지방선거를 통해 당선된 당선자들의 임기는 총 4년(2018.7.1.~2022.6.30.)이다. 최근 이슈가 되고 있는 대통령 4년 중임제 개헌안이 통과가 된다면 2022년에는 대선과 지방선거를 동시에 치르게 된다.', 

	23: '제 7회 전국동시지방선거를 마무리하며 다시 한 번 초심을 잃지 않는 국민을 위한 올바른 정치를 기대해본다.',
}

seq2type = {
	1:'cover', # 표지
	2:'rate', # 투표율 전체: 투표중, 마감이후
	3:'map', # 투표율 비교 / 전국 : 투표중, 마감이후
	4:'map', # 투표율 개인화 / 지역 : 투표중, 마감이후
	5:'map', # 투표율 개인화 / 후보 : 투표중, 마감이후
	6:'default', # 투표율 특이사항

	7:'rate', # 개표율 전체
	8:'map', # 개표율 비교 / 시도지사
	9:'map', # 개표율 비교 / 시군구청장
	10:'map', # 개표율 개인화 / 지역: 개표율 > 0, 개표율 = 0
	11:'map', # 개표율 개인화 / 선거: 개표율 > 0, 개표율 = 0
	12:'map', # 개표율 개인화 / 후보: 개표율 > 0, 개표율 = 0
	13:'default', # 개표율 특이사항

	14:'winner', # 득표율 전체
	15:'winner', # 득표율 시도지사
	16:'winner', # 득표율 시군구청장
	17:'graph', # 득표율 개인화 / 지역 : 확정이전, 확정이후
	18:'graph', # 득표율 개인화 / 후보 : 확정이전, 확정이후
	19:'graph', # 득표율 개인화 / 정당 : 확정이전, 확정이후
	20:'default', # 득표율 특이사항

	21:'default', # 당선확정
	22:'default', # transition
	23:'default', # 마무리
}