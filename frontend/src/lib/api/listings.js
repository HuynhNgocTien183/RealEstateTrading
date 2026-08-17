import client from './client';

export async function getListings(params = {}) {
  const res = await client.get('/listings/', { params });
  return res.data;
}

export async function getListingDetail(id) {
  const res = await client.get(`/listings/${id}/`);
  return res.data;
}

export async function createListing(data, imageFiles = []) {
  const formData = new FormData();

  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      formData.append(key, value);
    }
  });

  imageFiles.forEach((file) => {
    formData.append('images', file);
  });

  const res = await client.post('/listings/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function updateListing(id, data) {
  const res = await client.patch(`/listings/${id}/`, data);
  return res.data;
}

export async function deleteListing(id) {
  return client.delete(`/listings/${id}/`);
}

export async function getMyListings() {
  const res = await client.get('/listings/my_listings/');
  return res.data;
}

export async function getPendingListings() {
  const res = await client.get('/listings/pending/');
  return res.data;
}

export async function approveListing(id) {
  return client.post(`/listings/${id}/approve/`);
}


export async function rejectListing(id, reason) {
  return client.post(`/listings/${id}/reject/`, { reason });
}

export async function getRejectedListings() {
  const res = await client.get('/listings/rejected/');
  return res.data;
}

export async function uploadListingImages(id, imageFiles) {
  const formData = new FormData();
  imageFiles.forEach((file) => formData.append('images', file));
  const res = await client.post(`/listings/${id}/upload_images/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function deleteListingImage(listingId, imageId) {
  return client.delete(`/listings/${listingId}/images/${imageId}/`);
}