import json
from stock_util import StockUtil

class StockTag():
    def __init__(self):
        self.util = StockUtil()
        pass
    
    

    def add_tag(self,stock_id,tags_to_add):
        '''
        为某股票添加标签。
        add_tag('sz000002', 'ccc,ddd,eee')表示给万科添加3个标签，分别是ccc,ddd,eee。
        可以一次性添加多个标签，用逗号分隔。
        '''
        file_name = self.util.get_static_file_from_id(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        tags = []
        if 'tag' in info[stock_id]:
            tags = info[stock_id]['tag'].split(',')
        add_tag_list = tags_to_add.split(',')
        for t in add_tag_list:
            tags.append(t)
        info[stock_id]['tag'] = ','.join(tags)
        with open(file_name,'w') as f:
            f.write(json.dumps(info))
        
    def remove_tag(self,stock_id,tags_to_remove):
        '''
        删除某股票的某些标签。
        remove_tag('sz000002','a,a,a,ccc,ddd')表示把万科的a,ccc,ddd三个标签删除。
        '''
        file_name = self.util.get_static_file_from_id(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        tags = []
        if 'tag' in info[stock_id]:
            tags = info[stock_id]['tag'].split(',')
        else:
            print("There is no tag for this stock - %s..."%(stock_id))
            return 0
        remove_tag_list = tags_to_remove.split(',')
        for t in remove_tag_list:
            tags.remove(t)
        info[stock_id]['tag'] = ','.join(tags)
        with open(file_name,'w') as f:
            f.write(json.dumps(info))

    
    def get_tag(self,stock_id):
        '''
        获取某股票的所有标签。如果没有标签，返回空字符串。
        '''
        file_name = "./data/static/%s.static.json"%(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        tags = []
        if 'tag' in info[stock_id]:
            return info[stock_id]['tag']
        else:
            return ""

if __name__ == '__main__':
    t = StockTag()
    #t.add_tag('sz000002', 'ccc,ddd,eee')
    t.remove_tag('sz000002','a,a,a,ccc,ddd')
    print(t.get_tag('sz000002'))
    #t.add_propery('sh600000',{"tag1":{"ddd":"ccc"}})
    #t.remove_property('sh600000','tag1')
