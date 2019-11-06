/* -*- c++ -*- */
/* 
 * Copyright 2019 Alexandre Marquet.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */


#ifndef INCLUDED_LORA2_LORA_SOFT_DEWHITEN_H
#define INCLUDED_LORA2_LORA_SOFT_DEWHITEN_H

#include <lora2/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
  namespace lora2 {

    /*!
     * \brief <+description of block+>
     * \ingroup lora2
     *
     */
    class LORA2_API lora_soft_dewhiten : virtual public gr::tagged_stream_block
    {
     public:
      typedef boost::shared_ptr<lora_soft_dewhiten> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora2::lora_soft_dewhiten.
       *
       * To avoid accidental use of raw pointers, lora2::lora_soft_dewhiten's
       * constructor is in a private implementation
       * class. lora2::lora_soft_dewhiten::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint8_t CR, const std::string &len_tag_key);
    };

  } // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_SOFT_DEWHITEN_H */
