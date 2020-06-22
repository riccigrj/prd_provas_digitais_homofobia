        def get_word(hash,word)
          resp = false
          hash.each { |key,value|
            if value.is_a?(Hash)
              resp = get_word(value,word)
            end
            if !(value.nil?)&&(value.is_a?(String))
              if (value.downcase.include? word)
                resp = true
              end
            end
            break if resp
          }
          return resp
        end
        lgbtqia_words = event.get("[@metadata][lgbtqia_words]")
        event_hash = event.to_hash
        lgbtqia_words.each do |word|
         if (get_word(event_hash,word))
           if event.get("[word]").nil?
             event.set("word",[word])
           else
             event.set("word", [event.get("[word]"),word])
           end
         end
       end
